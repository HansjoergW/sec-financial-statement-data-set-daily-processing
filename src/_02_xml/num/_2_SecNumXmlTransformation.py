from _02_xml.num._1_SecNumXmlExtracting import SecNumXmlExtractor, SecNumExtraction, SecNumExtractContext, \
    SecNumExtractTag
from typing import Dict, List, Tuple, Union
from dataclasses import dataclass

import re
import calendar


@dataclass
class SecNumTransformedContext:
    id: str
    qtrs: int
    enddate: str
    segments: List[str]


@dataclass
class SecNumTransformedTag:
    tagname: str
    version: str
    valuetxt: str
    unitref: str
    ctxtref: str
    decimals: str


@dataclass
class SecNumTransformed:
    contexts_map: Dict[str, SecNumTransformedContext]
    tag_list: List[SecNumTransformedTag]


class SecNumXmlTransformer:

    find_year_regex = re.compile(r"\d\d\d\d")
    clean_tag_regex = re.compile(r"[{].*?[}]")

    def __init__(self):
        pass

    def _eval_versionyear(self, us_gaap_ns:str, ifrs_ns:str) -> str:
        versionyear = 0
        if us_gaap_ns:
            versionyear = self.find_year_regex.findall(us_gaap_ns)[0]

        if ifrs_ns:
            versionyear = self.find_year_regex.findall(ifrs_ns)[0]
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

    def _calculate_qtrs(self, year_start_s: str, month_start_s: str, year_end_s: str, month_end_s: str) -> int:
        """calculates the number of quartes between the start year/month and the end year/month"""
        year_start = int(year_start_s)
        year_end = int(year_end_s)
        month_start = int(month_start_s)
        month_end = int(month_end_s) + (year_end - year_start) * 12

        return int(round(float(month_end - month_start) / 3))

    def _transform_contexts(self, contexts: List[SecNumExtractContext]) -> Dict[str, SecNumTransformedContext]:
        context_map: Dict[str, SecNumTransformedContext] = {}

        for context in contexts:
            instanttxt = context.instanttxt
            startdatetxt = context.startdatetxt
            enddatetxt = context.enddatetxt

            qtrs:int
            enddate:str
            if instanttxt is None:
                enddate = self._find_last_day_of_month(enddatetxt)
                qtrs = self._calculate_qtrs(startdatetxt[0:4], startdatetxt[5:7], enddatetxt[0:4], enddatetxt[5:7])
            else:
                enddate = self._find_last_day_of_month(instanttxt)
                qtrs=0

            context_map[context.id] = SecNumTransformedContext(
                    id=context.id,
                    qtrs=qtrs,
                    enddate=enddate,
                    segments=context.segments)

        return context_map

    def _transform_tags(self, tags: List[SecNumExtractTag], versionyear: str, company_namespaces: List[str]) -> List[SecNumTransformedTag]:
        result: List[SecNumTransformedTag] = []

        for tag in tags:
            unitRef:str = tag.unitRef

            tagname = self.clean_tag_regex.sub("", tag.tagname)

            if unitRef in ["usd", "usdpershare", "u_iso4217usd"]:
                unitRef = "USD"
            elif unitRef == 'number':
                unitRef = 'pure'
            else:
                unitRef = unitRef.upper() # basically all entries are in to upper

            prefix = tag.prefix
            if prefix.startswith("ifrs"):
                prefix = "ifrs"

            if prefix in company_namespaces:
                version = 'company'
            else:
                version = prefix + "/" + str(versionyear)

            result.append(SecNumTransformedTag(
                tagname=tagname,
                version=version,
                valuetxt=tag.valuetxt,
                ctxtref=tag.ctxtRef,
                unitref=unitRef,
                decimals=tag.decimals
            ))

        return result

    def transform(self, adsh: str, data: SecNumExtraction) -> SecNumTransformed:
        versionyear = self._eval_versionyear(data.us_gaap_ns, data.ifrs_ns)

        contexts_map: Dict[str, SecNumTransformedContext] = self._transform_contexts(data.contexts)
        tag_list: List[SecNumTransformedTag] = self._transform_tags(data.tags, versionyear, data.company_namespaces)

        return SecNumTransformed(
            contexts_map=contexts_map,
            tag_list=tag_list
        )

