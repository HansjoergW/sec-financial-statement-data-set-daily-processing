from _02_xml.SecXmlParsingBase import SecXmlParserBase

import re
import pandas as pd

from lxml import etree
from typing import Dict, List, Tuple, Optional


# there are documents, which define the linke namespace diretcly in the node itself, without a prefix
# therefore it is necessary to add the link-ns without a prefix into the namespace map
# examples:
#  normal:         "d:/secprocessing/xml/2021-04-24/blpg-20200630_pre.xml"
#  with ns in tag: "d:/secprocessing/xml/2021-04-24/cspi-20200930_pre.xml"
# namespaces[""] = root.nsmap.get('link')


class SecPreXmlParser(SecXmlParserBase):
    """Parses the data of an Pre.Xml file and delivers the data in a similar format than the pre.txt
       contained in the financial statements dataset of the sex."""

    remove_unicode_tag_regex = re.compile(r" encoding=\"utf-8\"", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    link_regex = re.compile(r"(<link:)", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    link_end_regex = re.compile(r"(</link:)", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    xlink_regex = re.compile(r" xlink:", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    arcrole_regex = re.compile(r"http://www.xbrl.org/2003/arcrole/", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    role2003_regex = re.compile(r"http://www.xbrl.org/2003/role/", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    role2009_regex = re.compile(r"http://www.xbrl.org/2009/role/", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    # href_regex = re.compile(" href=\".*?#", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    type_clean_regex = re.compile(r"( type=\"locator\")|( type=\"arc\")", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    arcrole_parent_child_regex = re.compile(r" arcrole=\"parent-child\"", re.IGNORECASE + re.MULTILINE + re.DOTALL)

    default_ns_regex = re.compile(r"xmlns=\"http://www.xbrl.org/2003/linkbase\"", re.IGNORECASE)

    stmt_map:Dict[str,str] = {'Cover': 'CP',
                              'IncomeStatement': 'IS',
                              'StatementOfIncomeAndComprehensiveIncome': 'CI',
                              'StatementOfFinancialPosition': 'BS',
                              'StatementOfStockholdersEquity': 'EQ',
                              'StatementOfCashFlows': 'CF'
                              }

    def __init__(self):
        super(SecPreXmlParser, self).__init__("pre")
        pass

    def _strip_file(self, data: str) -> str:
        """removes unneeded content from the datastring, so that xml parsing will be faster"""
        data = self.remove_unicode_tag_regex.sub("", data)
        data = self.default_ns_regex.sub("", data) # some nodes define a default namespace.. that causes troubles
        data = self.link_regex.sub("<", data)
        data = self.link_end_regex.sub("</", data)
        data = self.xlink_regex.sub(" ", data)
        data = self.arcrole_regex.sub("", data)
        data = self.role2003_regex.sub("", data)
        data = self.role2009_regex.sub("", data)
        data = self.type_clean_regex.sub("", data)
        data = self.arcrole_parent_child_regex.sub("", data)

        return data

    def _get_prefered_label(self, presentation: etree._Element, namesapces: Dict[str,str]) -> Dict[str, str]:
        """just parse the presentationArc Elements and get the content of the preferredLabel for every location key"""

        dict:Dict[str, str] = {}
        arcs = presentation.findall('presentationArc', presentation.nsmap)

        for arc in arcs:
            child = arc.get('to')
            plabel = arc.get('preferredLabel')
            dict[child] = plabel

        return dict

    def _simple_list(self, presentation: etree._Element, namesapces: Dict[str,str]) -> List[Dict[str, str]]:
        locs = presentation.findall('loc', namesapces)
        prefered_label_dict = self._get_prefered_label(presentation, namesapces)

        result_list = []
        line = 0
        for loc in locs:
            key = loc.get("label")

            href_parts = loc.get("href").split('#')
            version = None
            if href_parts[0].startswith('http'):
                ns_parts = href_parts[0].split('/')
                version = ns_parts[3] + '/' + ns_parts[4]
            else:
                version = 'company'

            tag_info = href_parts[1].split("_")
            tag_prefix = tag_info[0]
            tag = tag_info[1]

            prefered_label = prefered_label_dict.get(key)
            negated = False
            if prefered_label:
                negated = "negated" in prefered_label

            entry = {"line": line, "version": version, "tag": tag, "negating": negated, "plabel": prefered_label, "key": key}
            result_list.append(entry)
            line += 1

        return result_list

    def _process_presentation(self, reportnr: int, presentation: etree._Element, namesapces: Dict[str,str]) -> List[Dict[str, str]]:
        entries = self._simple_list(presentation, namesapces)

        inpth = 0
        presentation_role = presentation.get('role',"").lower()
        if "parenthetical" in presentation_role:
            inpth = 1

        if len(entries) > 0:
            first_tag = entries[0]['tag']
            stmt = None

            for k, v in self.stmt_map.items():
                if k in first_tag:
                    stmt = v
            for entry in entries:
                entry['report'] = reportnr
                entry['stmt'] = stmt
                entry['inpth']  = inpth

        return entries

    def _process_presentations(self, root: etree._Element, rfile: str) -> pd.DataFrame:
        namespaces = root.nsmap

        presentation_links = root.findall('presentationLink', namespaces)

        report = 1
        all_entries: List[Dict[str, str]] = []
        for presentation in presentation_links:
            entries = self._process_presentation(report, presentation, namespaces)
            all_entries.extend(entries)
            report += 1

        df = pd.DataFrame(all_entries)
        df['rfile'] = rfile # filetype X for xml or H for html file
        return df

    def parse(self, data: str) -> pd.DataFrame:
        data = self._strip_file(data)
        data = bytes(bytearray(data, encoding='utf-8'))
        root = etree.fromstring(data)
        df = self._process_presentations(root, "-")
        return df

    def clean_for_financial_statement_dataset(self, df: pd.DataFrame, adsh: str = None) -> pd.DataFrame:
        df = df[~df.stmt.isnull()]
        df = df[df.line != 0].copy()
        df.drop(['plabel', 'key'], axis=1, inplace=True)
        df['adsh'] = adsh
        df.loc[df.version == 'company', 'version'] = adsh
        df.set_index(['adsh', 'tag','version', 'report', 'line', 'stmt'], inplace=True)
        return df