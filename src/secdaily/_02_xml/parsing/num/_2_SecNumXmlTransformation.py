import calendar
import re
from dataclasses import dataclass
from datetime import date
from typing import Dict, List

from secdaily._02_xml.parsing.num._1_SecNumXmlExtracting import (
    SecNumExtractContext,
    SecNumExtraction,
    SecNumExtractSegement,
    SecNumExtractTag,
    SecNumExtractUnit,
)


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
    id: str
    uom: str


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

    def _eval_versionyear(self, rel_ns_map: Dict[str, str]) -> Dict[str, str]:
        result: Dict[str, str] = {}

        for key, ns in rel_ns_map.items():
            versionyear = self.find_year_regex.findall(ns)[0]
            result[key] = versionyear

        return result

    def _find_close_last_day_of_month(self, datastr: str) -> str:
        """finds the last day of the month in the datestring with format yyyy-mm-dd
        and returns it as yyyymmdd"""
        yearstr = datastr[0:4]
        monthstr = datastr[5:7]
        daystr = datastr[8:]

        year = int(yearstr)
        month = int(monthstr)
        day = int(daystr)

        if day <= 15:
            if month == 1:
                month = 12
                year = year - 1
            else:
                month = month - 1

        last_day_of_month = calendar.monthrange(year, month)[1]
        return str(year) + str(month).zfill(2) + str(last_day_of_month).zfill(2)

    def _calculate_qtrs(
        self, year_start_s: str, month_start_s: str, day_start_s: str, year_end_s: str, month_end_s: str, day_end_s: str
    ) -> int:
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
        # in the mean, a quarter (leap year considered), a quarter has an average length of 365.25 days / 4
        # with this calculation, it is possible to reproduce the quarter length provided by sec
        return int(round(float(diff_days.days) * 4 / 365.25))

        # month_end = int(month_end_s) + (year_end - year_start) * 12
        # return int(round(float(month_end - month_start) / 3))

    def _clean_member_domain_from_coreg(self, coreg: str) -> str:
        if coreg.endswith("Member"):
            coreg = coreg[0 : len(coreg) - 6]

        if coreg.endswith("Domain"):
            coreg = coreg[0 : len(coreg) - 6]

        return coreg

    def _transform_contexts(self, contexts: List[SecNumExtractContext]) -> Dict[str, SecNumTransformedContext]:
        context_map: Dict[str, SecNumTransformedContext] = {}

        for context in contexts:
            instanttxt = context.instanttxt
            startdatetxt = context.startdatetxt
            enddatetxt = context.enddatetxt

            qtrs: int
            enddate: str
            if instanttxt is None:
                # todo: müsste man hier die anzahl qrts evtl. basierend auf find_close for start und enddate berechnen
                enddate = self._find_close_last_day_of_month(enddatetxt)
                qtrs = self._calculate_qtrs(
                    startdatetxt[0:4],
                    startdatetxt[5:7],
                    startdatetxt[8:10],
                    enddatetxt[0:4],
                    enddatetxt[5:7],
                    enddatetxt[8:10],
                )
            else:
                enddate = self._find_close_last_day_of_month(instanttxt)
                qtrs = 0

            coreg = ""
            isrelevant = False

            # a context is either relevant for the num.txt file, if there is no segment present
            if len(context.segments) == 0:
                isrelevant = True

            # ... or if there is just one LegalEntityAxis or StatementClassOfStockAxis segment present
            if len(context.segments) == 1:
                segment = context.segments[0]
                if segment.dimension == "dei:LegalEntityAxis":
                    isrelevant = True
                    coreg = segment.label
                    coreg = self._clean_member_domain_from_coreg(coreg)

                    if ":" in coreg:
                        coreg = coreg.split(":")[1]

                #
                if segment.dimension == "us-gaap:StatementClassOfStockAxis":
                    isrelevant = True

            context_map[context.id] = SecNumTransformedContext(
                id=context.id, qtrs=qtrs, enddate=enddate, coreg=coreg, isrelevant=isrelevant, segments=context.segments
            )

        return context_map

    def _transform_tags(
        self, tags: List[SecNumExtractTag], ns_years: Dict[str, str], company_namespaces: List[str]
    ) -> List[SecNumTransformedTag]:

        result: List[SecNumTransformedTag] = []

        for tag in tags:
            tagname = self.clean_tag_regex.sub("", tag.tagname)

            prefix = tag.prefix
            if prefix.startswith("ifrs"):
                prefix = "ifrs"

            if prefix in company_namespaces:
                version = "company"
            else:
                version = prefix + "/" + ns_years.get(prefix, "0000")

            result.append(
                SecNumTransformedTag(
                    tagname=tagname,
                    version=version,
                    valuetxt=tag.valuetxt,
                    ctxtref=tag.ctxtRef,
                    unitref=tag.unitRef,
                    decimals=tag.decimals,
                )
            )

        return result

    def _transform_units(self, units: List[SecNumExtractUnit]) -> Dict[str, SecNumTransformedUnit]:
        result: Dict[str, SecNumTransformedUnit] = {}

        for unit in units:
            unitid = unit.id
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
            elif denumerator == "shares":
                uom = numerator
            else:
                uom = numerator + "/" + denumerator

            result[unitid] = SecNumTransformedUnit(id=unitid, uom=uom)
        return result

    def transform(self, data: SecNumExtraction) -> SecNumTransformed:
        ns_years: Dict[str, str] = self._eval_versionyear(data.relevant_ns_map)

        contexts_map: Dict[str, SecNumTransformedContext] = self._transform_contexts(data.contexts)
        tag_list: List[SecNumTransformedTag] = self._transform_tags(data.tags, ns_years, data.company_namespaces)
        units_map: Dict[str, SecNumTransformedUnit] = self._transform_units(data.units)

        return SecNumTransformed(contexts_map=contexts_map, tag_list=tag_list, units_map=units_map)
