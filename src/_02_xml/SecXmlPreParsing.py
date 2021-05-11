from _02_xml.SecXmlParsingBase import SecXmlParserBase

import re
import pandas as pd

from lxml import etree
from typing import Dict, List
import logging


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
                              'DocumentAndEntityInformation': 'CP',
                              'IncomeStatement': 'IS',
                              'StatementOfIncomeAndComprehensiveIncome': 'CI',
                              'StatementOfFinancialPosition': 'BS',
                              'StatementOfStockholdersEquity': 'EQ',
                              'StatementOfCashFlows': 'CF',
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


    def _get_presentation_arc_content(self, presentation: etree._Element) -> Dict[str, Dict[str, str]]:
        # get order (line), and preferred_label (label, terselabel, totallabel, ...)
        result: Dict[str, Dict[str, str]] = {}
        arcs = presentation.findall('presentationArc', presentation.nsmap)
        if len(arcs) == 0:
            return result

        parent_child_dict: Dict[str, Dict[int, str]] = {}

        to_list: List[str] = []
        from_list: List[str] = []

        for arc in arcs:
            from_list.append(arc.get('from'))
            to_list.append(arc.get('to'))

        for arc in arcs:
            details: Dict[str,str] = {}
            to_tag = arc.get('to')
            from_tag = arc.get('from')
            prefered_label = arc.get('preferredLabel')

            # it is possible, that the same to_tag appears twice with different prefered_label
            # but this is only the case, if the to_tag is not also a from_tag
            if to_tag in from_list:
                key_tag = to_tag
            else:
                key_tag = to_tag + "." + prefered_label

            order_nr = int(float(arc.get('order'))) # some xmls have 0.0, 1.0 ... as order number instead of a pure int

            if from_tag not in parent_child_dict:
                parent_child_dict[from_tag] = {}

            parent_child_dict[from_tag][order_nr] = key_tag

            negated = False
            if prefered_label:
                negated = "negated" in prefered_label

            details['preferredLabel'] = prefered_label
            details['negating'] = negated

            result[key_tag] = details

        # line calculation
        root_node = set(from_list) - set(to_list)
        # there should be just one rootnote, at least in the presentations we are interested in
        if len(root_node) != 1:
            raise Exception("more than one root node")

        # the problem with the order number is, that the usage is not consistent.
        # in some reports, every child node starts with zero, in others, it starts with 1.
        # sometimes that is even mixed within the same presentation link.
        # example (temir-20200831_pre.xml)
        # other reports use a unique order number inside the presentation. (like gbt-20201231_pre.xml)
        # in this case, this would directly reflect the line number which would be the most simple way to calculate
        # so we first need to convert that in a simple ordered list which follows the defined order
        parent_child_ordered_list: Dict[str, List[str]] = {}
        for node_name, order_dict in parent_child_dict.items():
            child_list: List[str] = []
            for childkey in sorted(order_dict.keys()):
                child_list.append(order_dict.get(childkey))
            parent_child_ordered_list[node_name] = child_list


        # in order to calculate the line numbers, it is necessary walk along the parent-child relationship of the
        # presentation-arc while respecting the order number and starting with the root_node
        # in order to that, a recursive loop is used
        root_node = list(root_node)[0]

        node_path: List[str] = [root_node] # used to track the path

        # used to keep track of current processed child of these node
        # the problem is, that in some documents the order starts with a 0, in others with 1
        # in some documents, this is even mixed within the same presentation, so we need to figure out
        # what the start key is
        node_index: Dict[str, int] = {root_node : 0}

        line = 1
        while len(node_path) > 0:
            current_node = node_path[-1]
            current_index = node_index.get(current_node)
            current_children_ordered_list = parent_child_ordered_list[current_node]

            if current_index + 1 > len(current_children_ordered_list):
                node_path.pop()
                continue

            node_index[current_node] = current_index + 1

            child = current_children_ordered_list[current_index]

            result[child]['line'] = line

            grand_children = parent_child_ordered_list.get(child)
            if grand_children is not None:
                node_path.append(child)
                node_index[child] = 0

            line += 1

        return result

    def _get_loc_content(self, presentation: etree._Element) -> Dict[str, Dict[str, str]]:
        locs = presentation.findall('loc')

        result: Dict[str, Dict[str, str]] = {}

        for loc in locs:
            details: Dict[str,str] = {}
            label = loc.get("label")

            href_parts = loc.get("href").split('#')
            complete_tag = href_parts[1]
            version = None
            if href_parts[0].startswith('http'):
                ns_parts = href_parts[0].split('/')
                version = ns_parts[3] + '/' + ns_parts[4]
            else:
                version = 'company'

            tag_info = complete_tag.split("_")
            tag_prefix = tag_info[0]
            tag = tag_info[1]

            details['tag'] = tag
            details['version'] = version

            result[label] = details

        return result

    def _get_presentation_tag_info(self, presentation: etree._Element) -> List[Dict[str, str]]:

        presentation_arc_content = self._get_presentation_arc_content(presentation)
        loc_content = self._get_loc_content(presentation)

        result: List[Dict[str, str]] = []
        for k in presentation_arc_content.keys():
            details = {}
            loc_key = k.split('.')[0] # pre_arc key can consist out label + '.' + and preferred label
            loc_content_entry = loc_content[loc_key]
            pre_arc_content_entry = presentation_arc_content.get(k)

            details['version'] = loc_content_entry.get('version')
            details['tag'] = loc_content_entry.get('tag')

            if pre_arc_content_entry is not None:
                details['plabel'] = pre_arc_content_entry.get('preferredLabel')
                if pre_arc_content_entry.get('negating'):
                    details['negating'] = 1
                else:
                    details['negating'] = 0
                details['line'] = pre_arc_content_entry.get('line')
            else:
                details['line'] = 0

            result.append(details)

        return result

    def _find_statement_in_presentation(self, presentation: etree._Element) -> str:
        arcs = presentation.findall('presentationArc', presentation.nsmap)

        to_list: List[str] = []
        from_list: List[str] = []

        for arc in arcs:
            to_list.append(arc.get('to'))
            from_list.append(arc.get('from'))

        root_nodes = set(from_list) - set(to_list)
        for root_node in root_nodes:
            for k, v in self.stmt_map.items():
                if k in root_node:
                    return v
        return None

    def _process_presentation(self, reportnr: int, presentation: etree._Element) -> List[Dict[str, str]]:
        stmt = self._find_statement_in_presentation(presentation)
        if stmt is None: # if this presentation does not reflect a "real primary statement" it is ignored
            return []

        entries = self._get_presentation_tag_info(presentation)
        inpth = 0
        presentation_role = presentation.get('role',"").lower()
        if "parenthetical" in presentation_role:
            inpth = 1

        if len(entries) > 0:
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
            try:
                entries = self._process_presentation(report, presentation)
                if len(entries) > 0:
                    report += 1
            except Exception as err:
                # often a report contains a "presentation" entry with  more than one root node.
                # so far, we do not handle this, since that type of problem is mainly in presentations which do
                # not belong to the primary fincancial statements. so we ignore it
                logging.info("skipped report: {}".format(str(err)))
                continue

            all_entries.extend(entries)

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
        if len(df) == 0:
            return df
        df = df[~df.stmt.isnull()]
        df = df[df.line != 0].copy()
        df.drop(['plabel'], axis=1, inplace=True)
        df['adsh'] = adsh
        df.loc[df.version == 'company', 'version'] = adsh
        df.set_index(['adsh', 'tag','version', 'report', 'line', 'stmt'], inplace=True)
        return df