import re
from lxml import etree
from typing import Dict, List, Tuple, Union


class SecPreXmlExtractor():

    """ Preparses the xml content and returns a Dict, Tuple, List Structure with the relevant raw information"""

    remove_unicode_tag_regex = re.compile(r" encoding=\"utf-8\"", re.IGNORECASE + re.MULTILINE + re.DOTALL)
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

        return data

    def _get_locations(self, presentationLink: etree._Element) -> List[Dict[str, str]]:
        locs = presentationLink.findall('loc', presentationLink.nsmap)

        result: List[Dict[str, str]] = []
        for loc in locs:
            entry: Dict[str, str] = {}
            entry['label'] = loc.get('label')
            entry['href'] = loc.get('href')

            result.append(entry)

        return result

    def _get_presentationArcs(self, presentationLink: etree._Element) -> List[Dict[str, str]]:
        arcs = presentationLink.findall('presentationArc', presentationLink.nsmap)

        result: List[Dict[str, str]] = []
        for arc in arcs:
            entry: Dict[str, str] = {}
            entry['order'] = arc.get('order')
            entry['preferredLabel'] = arc.get('preferredLabel')
            entry['from'] = arc.get('from')
            entry['to'] = arc.get('to')

            result.append(entry)
        return result

    def _loop_presentationLink(self, root: etree._Element) -> Dict[int, Dict[str, Union[str, List[Dict[str, str]]]]]:
        namespaces = root.nsmap
        presentation_links = root.findall('presentationLink', namespaces)

        result: Dict[int, Dict[str, Union[str, List[Dict[str, str]]]]] = {}

        report = 0
        for presentation_link in presentation_links:
            details: Dict[str, Union[str, List[Dict[str, str]]]] = {}
            report += 1
            role: str = presentation_link.get("role")
            loc_list: List[Dict[str, str]] = self._get_locations(presentation_link)
            preArc_list: List[Dict[str, str]] = self._get_presentationArcs(presentation_link)

            details['role'] = role
            details['loc_list'] = loc_list
            details['preArc_list'] = preArc_list

            result[report] = details

        return result

    def preparexml(self, data: str) -> Dict[int,Dict[str, Union[str, List[Dict[str, str]]]]]:
        data = self._strip_file(data)
        data = bytes(bytearray(data, encoding='utf-8'))
        root = etree.fromstring(data)
        return self._loop_presentationLink(root)
