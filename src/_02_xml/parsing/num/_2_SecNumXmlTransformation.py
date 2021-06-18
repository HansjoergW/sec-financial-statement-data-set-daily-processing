from _02_xml.parsing.num._1_SecNumXmlExtracting import SecNumXmlExtractor, SecNumExtraction, SecNumExtractContext, \
    SecNumExtractTag, SecNumExtractSegement, SecNumExtractUnit
from typing import Dict, List, Tuple, Union
from dataclasses import dataclass

import re
import calendar
from datetime import date


@dataclass
class SecNumTransformedContext:
    id: str
    qtrs: int
    enddate: str
    coreg: str
    isrelevant: bool
    segments: List[SecNumExtractSegement]


@dataclass
class SecNumTransformedTag:
    tagname: str
    version: str
    valuetxt: str
    unitref: str
    ctxtref: str
    decimals: str


@dataclass
class SecNumTransformedUnit:
    id:str
    uom:str


@dataclass
class SecNumTransformed:
    contexts_map: Dict[str, SecNumTransformedContext]
    units_map: Dict[str, SecNumTransformedUnit]
    tag_list: List[SecNumTransformedTag]


class SecNumXmlTransformer:

    find_year_regex = re.compile(r"\d\d\d\d")
    clean_tag_regex = re.compile(r"[{].*?[}]")

    def __init__(self):
        pass

    def _eval_versionyear(self, us_gaap_ns:str, ifrs_ns:str, dei_ns:str) -> Dict[str, str]:
        result: Dict[str, str] = {}
        if us_gaap_ns:
            versionyear = self.find_year_regex.findall(us_gaap_ns)[0]
            result['us-gaap'] = versionyear

        if ifrs_ns:
            versionyear = self.find_year_regex.findall(ifrs_ns)[0]
            result['ifrs'] = versionyear

        if dei_ns:
            versionyear = self.find_year_regex.findall(dei_ns)[0]
            result['dei'] = versionyear

        return result

    def _eval_versionyear_dei(self, dei_ns:str) -> str:
        versionyear = 0

        if dei_ns:
            versionyear = self.find_year_regex.findall(dei_ns)[0]
        return versionyear

    def _find_last_day_of_month(self, datastr: str) -> str:
        """finds the last day of the month in the datestring with format yyyy-mm-dd
        and returns it as yyyymmdd """
        yearstr = datastr[0:4]
        monthstr = datastr[5:7]
        daystr = datastr[8:]

        year = int(yearstr)
        month = int(monthstr)

        last_day_of_month = calendar.monthrange(year, month)[1]
        return yearstr + monthstr + str(last_day_of_month).zfill(2)

    def _find_close_last_day_of_month(self, datastr: str) -> str:
        """finds the last day of the month in the datestring with format yyyy-mm-dd
        and returns it as yyyymmdd """
        yearstr = datastr[0:4]
        monthstr = datastr[5:7]
        daystr = datastr[8:]

        year = int(yearstr)
        month = int(monthstr)
        day = int(daystr)

        if day < 15:
            if month == 1:
                month = 12
                year = year -1
            else:
                month = month - 1

        last_day_of_month = calendar.monthrange(year, month)[1]
        return str(year) + str(month).zfill(2) + str(last_day_of_month).zfill(2)

    def _calculate_qtrs(self, year_start_s: str, month_start_s: str, day_start_s: str, year_end_s: str, month_end_s: str, day_end_s: str) -> int:
        """calculates the number of quartes between the start year/month and the end year/month"""
        year_start = int(year_start_s)
        year_end = int(year_end_s)
        month_start = int(month_start_s)
        month_end = int(month_end_s)
        day_start = int(day_start_s)
        day_end = int(day_end_s)

        start_date = date(year_start, month_start, day_start)
        end_date = date(year_end, month_end, day_end)

        diff_days = end_date - start_date
        return int(round(float(diff_days.days) / 91))

        # month_end = int(month_end_s) + (year_end - year_start) * 12
        # return int(round(float(month_end - month_start) / 3))

    def _transform_contexts(self, contexts: List[SecNumExtractContext], company_namespaces: List[str]) -> Dict[str, SecNumTransformedContext]:
        context_map: Dict[str, SecNumTransformedContext] = {}

        for context in contexts:
            instanttxt = context.instanttxt
            startdatetxt = context.startdatetxt
            enddatetxt = context.enddatetxt

            qtrs:int
            enddate:str
            if instanttxt is None:
                enddate = self._find_close_last_day_of_month(enddatetxt)
                qtrs = self._calculate_qtrs(startdatetxt[0:4], startdatetxt[5:7], startdatetxt[8:10], enddatetxt[0:4], enddatetxt[5:7], enddatetxt[8:10])
            else:
                enddate = self._find_close_last_day_of_month(instanttxt)
                qtrs=0

            coreg = ""
            isrelevant = False

            # a context is either relevant for the num.txt file, if there is no segment present
            if len(context.segments) == 0:
                isrelevant = True

            # ... or if there is just one LegalEntityAxis segment present
            #for segment in context.segments:
            if len(context.segments) == 1:
                segment = context.segments[0]
                if segment.dimension == "dei:LegalEntityAxis":
                    isrelevant = True
                    coreg = segment.label
                    if coreg.endswith("Member"):
                        coreg = coreg.replace("Member", "")

                    if coreg.endswith("Domain"):
                        coreg = coreg.replace("Domain", "")

                    for company_namespace in company_namespaces:
                        coreg = coreg.replace(company_namespace + ":", "")

            context_map[context.id] = SecNumTransformedContext(
                id=context.id,
                qtrs=qtrs,
                enddate=enddate,
                coreg=coreg,
                isrelevant=isrelevant,
                segments=context.segments)

        return context_map

    def _transform_tags(self, tags: List[SecNumExtractTag], ns_years: Dict[str, str], company_namespaces: List[str]) -> List[SecNumTransformedTag]:
        result: List[SecNumTransformedTag] = []

        for tag in tags:
            tagname = self.clean_tag_regex.sub("", tag.tagname)

            prefix = tag.prefix
            if prefix.startswith("ifrs"):
                prefix = "ifrs"

            if prefix in company_namespaces:
                version = 'company'
            else:
                version = prefix + "/" + ns_years.get(prefix, "0000")

            result.append(SecNumTransformedTag(
                tagname=tagname,
                version=version,
                valuetxt=tag.valuetxt,
                ctxtref=tag.ctxtRef,
                unitref=tag.unitRef,
                decimals=tag.decimals
            ))

        return result

    def _transform_units(self, units: List[SecNumExtractUnit]) -> Dict[str, SecNumTransformedUnit]:
        result: Dict[str, SecNumTransformedUnit] = {}

        for unit in units:
            id = unit.id
            measure = unit.measure
            numerator = unit.numerator
            denumerator = unit.denumerator

            if measure and (":" in measure):
                measure = measure.split(":")[1]
            if numerator and (":" in numerator):
                numerator = numerator.split(":")[1]
            if denumerator and (":" in denumerator):
                denumerator = denumerator.split(":")[1]

            uom: str
            if measure is not None:
                uom = measure
            elif denumerator == 'shares':
                uom = numerator
            else:
                uom = numerator + '/' + denumerator

            result[id] = SecNumTransformedUnit(id=id, uom=uom)
        return result

    def transform(self, adsh: str, data: SecNumExtraction) -> SecNumTransformed:
        ns_years:Dict[str, str] = self._eval_versionyear(data.us_gaap_ns, data.ifrs_ns, data.dei_ns)

        contexts_map: Dict[str, SecNumTransformedContext] = self._transform_contexts(data.contexts, data.company_namespaces)
        tag_list: List[SecNumTransformedTag] = self._transform_tags(data.tags, ns_years, data.company_namespaces)
        units_map: Dict[str, SecNumTransformedUnit] = self._transform_units(data.units)

        return SecNumTransformed(
            contexts_map=contexts_map,
            tag_list=tag_list,
            units_map= units_map
        )


    #
    # # ISO4217-USD
    # # ISO4217-USD-PER-UTR-BBL
    # # ISO4217-USD-PER-UTR-MCF
    # # ISO4217-USD-PER-XBRLI-SHARES
    # # ISO4217_USD_PER_SHARES
    # # ISO4217_USD_XBRLI_SHARES
    # # U_ISO4217AUD
    # # U_ISO4217CAD_XBRLISHARES
    # def _check_for_iso_uom(self, unitRef:str) -> Union[None, str]:
    #     if unitRef.startswith("ISO4217"):
    #         return unitRef[8:12]
    #     if unitRef.startswith("U_ISO4217"):
    #         return unitRef[9:13]
    #     return None
    #
    # def _check_for_unit_divide(self, unitRef:str) -> Union[None, str]:
    #     if unitRef.startswith("UNIT_DIVIDE_"):
    #         return unitRef.split('_')[2]
    #     return None
    #
    # def _check_for_unit_standard(self, unitRef:str) -> Union[None, str]:
    #     if unitRef.startswith("UNIT_STANDARD_"):
    #         return unitRef.split('_')[2]
    #     return None
    #
    # def _check_for_unit(self, unitRef:str) -> Union[None, str]:
    #     if unitRef.startswith("UNIT_"):
    #         return unitRef.split('_')[1]
    #     return None
    #
    # # CADPERSHARE immer mit 3 Zeichen vor dran
    # # CADPERSHARES
    # # CADPSHARES
    # # CAD_PER_SHARE
    # pershare_postfixes = ['PERSHARE', 'PERSHARES','PSHARES','PSHARE','_PER_SHARE']
    # def _check_for_per_schare_postfix(self, unitRef:str) -> Union[None, str]:
    #     for pershare_pf in self.pershare_postfixes:
    #         if unitRef.endswith(pershare_pf):
    #             return unitRef[0:3]
    #     return None
    #
    #
    # known_prefixes = ['U_XBRLI', 'U_NTGR']
    # def _check_for_known_prefixes(self, unitRef:str) -> Union[None, str]:
    #
    #     for known_prefix in self.known_prefixes:
    #         if known_prefix in unitRef:
    #             return unitRef.replace(known_prefix, "")
    #     return None
    #
    #
    # def _evaluate_unitRef(self, unitRef: str) -> str:
    #     unitRef = unitRef.upper()
    #
    #     evaluated = self._check_for_iso_uom(unitRef)
    #     if evaluated:
    #         return evaluated
    #
    #     evaluated = self._check_for_unit_divide(unitRef)
    #     if evaluated:
    #         return evaluated
    #
    #     evaluated = self._check_for_unit_standard(unitRef)
    #     if evaluated:
    #         return evaluated
    #
    #     evaluated = self._check_for_per_schare_postfix(unitRef)
    #     if evaluated:
    #         return evaluated
    #
    #
    #     # old checks
    #     if unitRef == 'number':
    #         unitRef = 'pure'
    #     elif len(unitRef) == 3:
    #         unitRef = unitRef.upper() # basically all currency entries are in to upper
    #     else:
    #         unitRef = unitRef.lower()
    #
    #     return unitRef
