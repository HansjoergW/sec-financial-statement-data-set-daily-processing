import re
from dataclasses import dataclass
from typing import List

from lxml import etree


@dataclass
class SecLabExtractLabelArcDetails:
    order: str
    from_entry: str
    to_entry: str
    role: str


@dataclass
class SecLabExtractLabelDetails:
    label: str
    role: str
    type: str
    text: str
    lang: str


@dataclass
class SecLabExtractLabelLocDetails:
    label: str
    href: str


@dataclass
class SecLabLabelLink:
    labels: List[SecLabExtractLabelDetails]
    arcs: List[SecLabExtractLabelArcDetails]
    locs: List[SecLabExtractLabelLocDetails]


class SecLabXmlExtractor:
    """Preparses the xml content and returns a Dict, Tuple, List Structure with the relevant raw information"""

    remove_unicode_tag_regex = re.compile(r" encoding=\"utf-8\"", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    default_ns_regex = re.compile(r"xmlns=\"http://www.xbrl.org/2003/linkbase\"", re.IGNORECASE)
    link_regex = re.compile(r"(<link:)", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    link_end_regex = re.compile(r"(</link:)", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    xlink_regex = re.compile(r" xlink:", re.IGNORECASE + re.MULTILINE + re.DOTALL)

    arcrole_regex = re.compile(r"http://www.xbrl.org/2003/arcrole/", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    role2003_regex = re.compile(r"http://www.xbrl.org/2003/role/", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    role2009_regex = re.compile(r"http://www.xbrl.org/2009/role/", re.IGNORECASE + re.MULTILINE + re.DOTALL)

    type_clean_regex = re.compile(r"( type=\"locator\")|( type=\"arc\")", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    arcrole_parent_child_regex = re.compile(r" arcrole=\"parent-child\"", re.IGNORECASE + re.MULTILINE + re.DOTALL)

    xml_lang_regex = re.compile(r"xml:lang", re.IGNORECASE)

    def __init__(self):
        pass

    def _strip_file(self, data: str) -> str:
        """removes unneeded content from the datastring, so that xml parsing will be faster"""
        data = self.remove_unicode_tag_regex.sub("", data)
        data = self.default_ns_regex.sub("", data)  # some nodes define a default namespace.. that causes troubles
        data = self.link_regex.sub("<", data)
        data = self.link_end_regex.sub("</", data)
        data = self.xlink_regex.sub(" ", data)
        data = self.arcrole_regex.sub("", data)
        data = self.role2003_regex.sub("", data)
        data = self.role2009_regex.sub("", data)
        data = self.type_clean_regex.sub("", data)
        data = self.arcrole_parent_child_regex.sub("", data)

        data = self.xml_lang_regex.sub("lang", data)
        return data

    def _read_structure(self, root: etree._Element) -> SecLabLabelLink:
        "reads the xml content into a structured format"

        namespaces = root.nsmap
        label_link_el = root.find("labelLink", namespaces)
        label_els = label_link_el.findall("label", namespaces)

        labels: List[SecLabExtractLabelDetails] = [
            SecLabExtractLabelDetails(
                label=label.get("label"),
                role=label.get("role"),
                type=label.get("type"),
                text=label.text,
                lang=label.get("lang"),
            )
            for label in label_els
        ]

        arc_els = label_link_el.findall("labelArc", namespaces)
        arcs: List[SecLabExtractLabelArcDetails] = [
            SecLabExtractLabelArcDetails(
                order=arc.get("order"), from_entry=arc.get("from"), to_entry=arc.get("to"), role=arc.get("role")
            )
            for arc in arc_els
        ]

        loc_els = label_link_el.findall("loc", namespaces)
        locs: List[SecLabExtractLabelLocDetails] = [
            SecLabExtractLabelLocDetails(label=loc.get("label"), href=loc.get("href")) for loc in loc_els
        ]

        label_details = SecLabLabelLink(labels=labels, arcs=arcs, locs=locs)
        return label_details

    def extract(self, data: str) -> SecLabLabelLink:
        data = self._strip_file(data)
        byte_data: bytes = bytes(bytearray(data, encoding="utf-8"))
        root = etree.fromstring(byte_data, parser=None)
        return self._read_structure(root)
