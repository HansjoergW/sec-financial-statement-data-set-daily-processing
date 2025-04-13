import re

from lxml import etree

# @dataclass
# class SecPreExtractPresentationArcDetails():
#     order: str
#     preferredLabel: str
#     from_entry: str
#     to_entry: str


# @dataclass
# class SecPreExtractLocationDetails():
#     label: str
#     href: str


# @dataclass
# class SecPreExtractPresentationLink():
#     role: str
#     title: str
#     loc_list: List[SecPreExtractLocationDetails]
#     preArc_list: List[SecPreExtractPresentationArcDetails]


class SecHtmXmlExtractor:
    """Preparses the xml content and returns a Dict, Tuple, List Structure with the relevant raw information"""

    remove_unicode_tag_regex = re.compile(r" encoding=\"utf-8\"", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    remove_ix_header_regex = re.compile(r"<ix:header>.*?</ix:header>", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    remove_style_content_regex = re.compile(r'(?<=style=")[^"]*(?=")')
    remove_empty_style_regex = re.compile(r"( style=\"\")", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    remove_colspan_content_regex = re.compile(r'(?<=colspan=")[^"]*(?=")')
    remove_empty_colspan_regex = re.compile(r"( colspan=\"\")", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    remove_span_attributes_regex = re.compile(r"<span\s+[^>]*>", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    remove_div_attributes_regex = re.compile(r"<div\s+[^>]*>", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    remove_span_160_regex = re.compile(r"(<span>&#160;</span>)")
    remove_empty_span_regex = re.compile(r"(<span> </span>)|(<span></span>)")
    remove_empty_ps_regex = re.compile(r"<p></p>")
    remove_dollar_ps_regex = re.compile(r"<p>\$</p>")
    remove_dash_ps_regex = re.compile(r"<p>\-</p>")
    remove_class_content_regex = re.compile(r'(?<=class=")[^"]*(?=")')
    remove_empty_class_regex = re.compile(r"( class=\"\")", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    remove_empty_tds_regex = re.compile(r"(<td></td>)|(<td/>)")
    remove_span_tags_regex = re.compile(r"(<span>)|(</span>)")
    remove_div_tags_regex = re.compile(r"(<div>)|(</div>)")
    remove_empty_lines_regex = re.compile(r"^\s*$\n", re.MULTILINE)

    link_regex = re.compile(r"(<link:)", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    link_end_regex = re.compile(r"(</link:)", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    xlink_regex = re.compile(r" xlink:", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    arcrole_regex = re.compile(r"http://www.xbrl.org/2003/arcrole/", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    role2003_regex = re.compile(r"http://www.xbrl.org/2003/role/", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    role2009_regex = re.compile(r"http://www.xbrl.org/2009/role/", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    type_clean_regex = re.compile(r"( type=\"locator\")|( type=\"arc\")", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    arcrole_parent_child_regex = re.compile(r" arcrole=\"parent-child\"", re.IGNORECASE + re.MULTILINE + re.DOTALL)

    default_ns_regex = re.compile(r"xmlns=\"http://www.xbrl.org/2003/linkbase\"", re.IGNORECASE)

    def __init__(self):
        pass

    def _strip_file(self, data: str) -> str:
        """removes unneeded content from the datastring, so that xml parsing will be faster"""
        data = self.remove_ix_header_regex.sub("", data)
        data = self.remove_style_content_regex.sub("", data)
        data = self.remove_empty_style_regex.sub("", data)
        data = self.remove_colspan_content_regex.sub("", data)
        data = self.remove_empty_colspan_regex.sub("", data)
        data = self.remove_span_attributes_regex.sub("", data)
        data = self.remove_div_attributes_regex.sub("", data)
        data = self.remove_span_160_regex.sub("", data)
        data = self.remove_empty_span_regex.sub("", data)
        data = self.remove_empty_ps_regex.sub("", data)
        data = self.remove_class_content_regex.sub("", data)
        data = self.remove_empty_class_regex.sub("", data)
        data = self.remove_span_tags_regex.sub("", data)
        data = self.remove_div_tags_regex.sub("", data)
        data = self.remove_dollar_ps_regex.sub("", data)
        data = self.remove_dash_ps_regex.sub("", data)
        data = self.remove_empty_tds_regex.sub("", data)
        data = self.remove_empty_lines_regex.sub("", data)

        # next colspan -> before td remove
        # next empty lines removen

        # remove empty divs -> gibt es nicht empty divs?
        # consider to remove  completely "<span...>" und "</span>"

        # data = self.remove_unicode_tag_regex.sub("", data)
        # data = self.default_ns_regex.sub("", data)  # some nodes define a default namespace.. that causes troubles
        # data = self.link_regex.sub("<", data)
        # data = self.link_end_regex.sub("</", data)
        # data = self.xlink_regex.sub(" ", data)
        # data = self.arcrole_regex.sub("", data)
        # data = self.role2003_regex.sub("", data)
        # data = self.role2009_regex.sub("", data)
        # data = self.type_clean_regex.sub("", data)
        # data = self.arcrole_parent_child_regex.sub("", data)

        return data

    # def _get_locations(self, presentationLink: etree._Element) -> List[SecPreExtractLocationDetails]:
    #     locs = presentationLink.findall('loc', presentationLink.nsmap)

    #     result: List[SecPreExtractLocationDetails] = []
    #     for loc in locs:
    #         entry: SecPreExtractLocationDetails = SecPreExtractLocationDetails(
    #             label=loc.get('label'),
    #             href=loc.get('href'))

    #         result.append(entry)

    #     return result

    # def _get_presentationArcs(self, presentationLink: etree._Element) -> List[SecPreExtractPresentationArcDetails]:
    #     arcs = presentationLink.findall('presentationArc', presentationLink.nsmap)

    #     result: List[SecPreExtractPresentationArcDetails] = []
    #     for arc in arcs:
    #         entry = SecPreExtractPresentationArcDetails(
    #             order=arc.get('order'),
    #             preferredLabel=arc.get('preferredLabel', ''),  # if missing, use a ''
    #             from_entry=arc.get('from'),
    #             to_entry=arc.get('to'))

    #         result.append(entry)
    #     return result

    # def _loop_presentationLink(self, root: etree._Element) -> Dict[int, SecPreExtractPresentationLink]:
    #     namespaces = root.nsmap
    #     presentation_links = root.findall('presentationLink', namespaces)

    #     result: Dict[int, SecPreExtractPresentationLink] = {}

    #     report = 0
    #     for presentation_link in presentation_links:
    #         report += 1

    #         details: SecPreExtractPresentationLink = SecPreExtractPresentationLink(
    #             role=presentation_link.get("role"),
    #             title=presentation_link.get("title"),
    #             loc_list=self._get_locations(presentation_link),
    #             preArc_list=self._get_presentationArcs(presentation_link))

    #         result[report] = details

    #     return result

    def extract(self, data: str):  # -> Dict[int, SecPreExtractPresentationLink]:
        data = self._strip_file(data)
        byte_data: bytes = bytes(bytearray(data, encoding="utf-8"))
        root = etree.fromstring(byte_data, parser=None) #  # noqa: F841 pylint: disable=unused-variable

        # continue
