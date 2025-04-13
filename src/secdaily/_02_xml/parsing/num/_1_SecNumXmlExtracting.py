import re
from dataclasses import dataclass
from typing import Dict, List, Union

from lxml import etree


@dataclass
class SecNumExtractSegement:
    label: str
    dimension: str


@dataclass
class SecNumExtractContext:
    instanttxt: Union[str, None]
    startdatetxt: Union[str, None]
    enddatetxt: Union[str, None]
    id: str
    segments: List[SecNumExtractSegement]


@dataclass
class SecNumExtractTag:
    tagname: str
    prefix: str
    valuetxt: str
    decimals: str
    ctxtRef: str
    unitRef: str


@dataclass
class SecNumExtractUnit:
    id: str
    measure: str
    denumerator: str
    numerator: str


@dataclass
class SecNumExtraction:
    company_namespaces: List[str]
    relevant_ns_map: Dict[str, str]
    contexts: List[SecNumExtractContext]
    tags: List[SecNumExtractTag]
    units: List[SecNumExtractUnit]


class SecNumXmlExtractor:

    # reports who's num file is part of the report use a "xbrli" prefix for all tags
    # reports for which the "num"xml has been created from the html don't use such a tag
    xbrli_prefix_regex = re.compile(r"xbrli:", re.IGNORECASE + re.DOTALL)

    period_regex = re.compile(r"<period>|(</period>)", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    entity_regex = re.compile(r"<entity>|(</entity>)", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    identifier_regex = re.compile(r"(<identifier).*?(</identifier>)", re.IGNORECASE + re.MULTILINE + re.DOTALL)

    xbrlns_regex = re.compile(r"xmlns=\".*?\"", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    link_regex = re.compile(r"<link.*?>", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    link_end_regex = re.compile(r"</link.*?>", re.IGNORECASE + re.MULTILINE + re.DOTALL)

    remove_unicode_tag_regex = re.compile(r" encoding=\"utf-8\"", re.IGNORECASE + re.MULTILINE + re.DOTALL)

    relevant_ns = ["us-gaap", "ifrs_full", "dei", "srt", "stpr"]

    def __init__(self):
        pass

    def _strip_file(self, data: str) -> str:
        """removes unneeded content from the datastring, so that xml parsing will be faster"""
        data = self.xbrli_prefix_regex.sub("", data)
        data = self.identifier_regex.sub("", data)
        data = self.period_regex.sub("", data)
        data = self.entity_regex.sub("", data)
        data = self.xbrlns_regex.sub("", data)  # clear xbrlns, so it is easier to parse
        data = self.link_regex.sub("", data)
        data = self.link_end_regex.sub("", data)
        data = self.remove_unicode_tag_regex.sub("", data)

        return data

    def _find_company_namespaces(self, root: etree._Element) -> List[str]:
        official = ["xbrl.org", "sec.gov", "fasb.org", "w3.org", "xbrl.ifrs.org"]
        company_namespaces = []
        for key, value in root.nsmap.items():
            if not any(x in value for x in official):
                company_namespaces.append(key)
        return company_namespaces

    def _read_contexts(self, root: etree._Element) -> List[SecNumExtractContext]:
        contexts = root.findall("context", root.nsmap)
        result: List[SecNumExtractContext] = []

        for context in contexts:
            instanttxt = None
            startdatetxt = None
            enddatetxt = None

            # generally, we are mainly interested in the contexts without a segment
            # however, the segment might be deliver interesting inside in future analysis
            segments = list(context.findall(".//*[@dimension]", root.nsmap))
            segments_list = []
            for segment in segments:
                segment_label = segment.text
                segment_dim = segment.get("dimension")
                segments_list.append(SecNumExtractSegement(label=segment_label, dimension=segment_dim))

            ctx_id = context.get("id")
            instant = context.find("instant", root.nsmap)
            if instant is not None:
                instanttxt = instant.text

            startdate = context.find("startDate", root.nsmap)
            if startdate is not None:
                startdatetxt = startdate.text

            enddate = context.find("endDate", root.nsmap)
            if enddate is not None:
                enddatetxt = enddate.text

            result.append(
                SecNumExtractContext(
                    instanttxt=instanttxt,
                    startdatetxt=startdatetxt,
                    enddatetxt=enddatetxt,
                    id=ctx_id,
                    segments=segments_list,
                )
            )

        return result

    def _read_units(self, root: etree._Element) -> List[SecNumExtractUnit]:
        units = root.findall("unit", root.nsmap)
        result: List[SecNumExtractUnit] = []

        for unit in units:
            unit_id = unit.get("id")
            measure = None
            denumerator = None
            numerator = None
            measure_node = unit.find("measure", root.nsmap)
            divide_node = unit.find("divide", root.nsmap)

            if measure_node is not None:
                measure = measure_node.text
            elif divide_node is not None:
                numerator_child = divide_node.find("unitNumerator/measure", root.nsmap)
                numerator = numerator_child.text
                denumerator_child = divide_node.find("unitDenominator/measure", root.nsmap)
                denumerator = denumerator_child.text

            result.append(SecNumExtractUnit(id=unit_id, measure=measure, denumerator=denumerator, numerator=numerator))
        return result

    def _read_tags(self, root: etree._Element) -> List[SecNumExtractTag]:

        tags = list(root.findall(".//*[@unitRef]"))
        tags_secexchange = list(root.findall(".//dei:SecurityExchangeName", root.nsmap))
        tags_tradingsymbol = list(root.findall(".//dei:TradingSymbol", root.nsmap))
        tags_fiscalyearend = list(root.findall(".//dei:CurrentFiscalYearEndDate", root.nsmap))

        tags.extend(tags_secexchange)
        tags.extend(tags_tradingsymbol)
        tags.extend(tags_fiscalyearend)

        result: List[SecNumExtractTag] = []

        for tag in tags:
            value_text = tag.text
            prefix = tag.prefix
            decimals = tag.get("decimals")
            ctxtRef = tag.get("contextRef")
            unitRef = tag.get("unitRef")

            result.append(
                SecNumExtractTag(
                    tagname=tag.tag,
                    valuetxt=value_text,
                    prefix=prefix,
                    decimals=decimals,
                    ctxtRef=ctxtRef,
                    unitRef=unitRef,
                )
            )

        return result

    def _extract_data(self, root: etree._Element) -> SecNumExtraction:
        company_namespaces = self._find_company_namespaces(root)

        rel_ns_map: Dict[str, str] = {}
        for rel_ns in self.relevant_ns:
            ns = root.nsmap.get(rel_ns, None)
            if ns:
                rel_ns_map[rel_ns] = ns

        contexts: List[SecNumExtractContext] = self._read_contexts(root)
        tags: List[SecNumExtractTag] = self._read_tags(root)
        units: List[SecNumExtractUnit] = self._read_units(root)

        return SecNumExtraction(
            company_namespaces=company_namespaces, relevant_ns_map=rel_ns_map, contexts=contexts, tags=tags, units=units
        )

    def extract(self, data: str) -> SecNumExtraction:
        data = self._strip_file(data)
        data_bytes = bytes(bytearray(data, encoding="utf-8"))
        parser = etree.XMLParser(huge_tree=True)
        root: etree._Element = etree.fromstring(data_bytes, parser)

        return self._extract_data(root)
