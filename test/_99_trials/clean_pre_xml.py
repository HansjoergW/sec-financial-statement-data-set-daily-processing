import re
from lxml import etree
import calendar
import pandas as pd
from typing import Dict, List, Tuple

file = "c:/ieu/projects/sec_processing/data/aapl-20200926_pre.xml"
target_pre_clean_xml = "c:/ieu/projects/sec_processing/data/aapl-20200926_pre-clean.xml"

remove_unicode_tag_regex = re.compile(r" encoding=\"utf-8\"", re.IGNORECASE + re.MULTILINE + re.DOTALL)
link_regex = re.compile(r"(<link:)", re.IGNORECASE + re.MULTILINE + re.DOTALL)
link_end_regex = re.compile(r"(</link:)", re.IGNORECASE + re.MULTILINE + re.DOTALL)
xlink_regex = re.compile(r" xlink:", re.IGNORECASE + re.MULTILINE + re.DOTALL)
arcrole_regex = re.compile(r"http://www.xbrl.org/2003/arcrole/", re.IGNORECASE + re.MULTILINE + re.DOTALL)
role2003_regex = re.compile(r"http://www.xbrl.org/2003/role/", re.IGNORECASE + re.MULTILINE + re.DOTALL)
role2009_regex = re.compile(r"http://www.xbrl.org/2009/role/", re.IGNORECASE + re.MULTILINE + re.DOTALL)
href_regex = re.compile(" href=\".*?#", re.IGNORECASE + re.MULTILINE + re.DOTALL)
type_clean_regex = re.compile("( type=\"locator\")|( type=\"arc\")", re.IGNORECASE + re.MULTILINE + re.DOTALL)
arcrole_parent_child_regex = re.compile(" arcrole=\"parent-child\"", re.IGNORECASE + re.MULTILINE + re.DOTALL)


stmt_map:Dict[str,str] = {'Cover': 'CP',
                          'IncomeStatement': 'IS',
                          'StatementOfIncomeAndComprehensiveIncome': 'CI',
                          'StatementOfFinancialPosition': 'BS',
                          'StatementOfStockholdersEquity': 'EQ',
                          'StatementOfCashFlows': 'CF'
                          }



def _strip_file(data: str) -> str:
    """removes unneeded content from the datastring, so that xml file is easier to understand and xml parsing will be faster"""
    data = remove_unicode_tag_regex.sub("", data)
    data = link_regex.sub("<", data)
    data = link_end_regex.sub("</", data)
    data = xlink_regex.sub(" ", data)
    data = arcrole_regex.sub("", data)
    data = role2003_regex.sub("", data)
    data = role2009_regex.sub("", data)
    data = href_regex.sub(" href=\"", data)
    data = type_clean_regex.sub("", data)
    data = arcrole_parent_child_regex.sub("", data)
    return data


def write_to_file(filename, data):
    with open(filename, "w", encoding="utf8") as f:
        f.write(data)
        f.close()


def create_loc_map(presentation: etree._Element) -> Tuple[str,Dict[str, Tuple[str, str, List[str]]]]:
    locs  = list(presentation.iter('loc'))
    loc_dict = {}
    first_key = None
    for loc in locs:
        key = loc.get("label")
        if not first_key:
            first_key = key
        tag_info = loc.get("href").split("_")
        tag_prefix = tag_info[0]
        tag = tag_info[1]
        loc_dict[key] = (tag_prefix, tag, [])

    return first_key, loc_dict


def fill_parent_child(presentation: etree._Element, locmap: Dict[str, Tuple[str, str, List[str]]]):
    arcs = list(presentation.iter('presentationArc'))

    for arc in arcs:
        order = arc.get('order')
        parent = arc.get('from')
        child = arc.get('to')
        plabel = arc.get('preferredLabel')
        locmap[parent][2].append((child, order, plabel))


def get_prefered_label(presentation: etree._Element) -> Dict[str, str]:

    dict:Dict[str, str] = {}
    arcs = list(presentation.iter('presentationArc'))

    for arc in arcs:
        child = arc.get('to')
        plabel = arc.get('preferredLabel')
        dict[child] = plabel

    return dict


def simple_list(presentation: etree._Element) -> List[Dict[str, str]]:
    locs  = list(presentation.iter('loc'))
    prefered_label_dict = get_prefered_label(presentation)

    result_list = []
    line = 0
    for loc in locs:
        key = loc.get("label")

        tag_info = loc.get("href").split("_")
        tag_prefix = tag_info[0]
        tag = tag_info[1]

        prefered_label = prefered_label_dict.get(key)
        negated = False
        if prefered_label:
            negated = "negated" in prefered_label

        entry = {"line": line, "version": tag_prefix, "tag": tag, "negated": negated, "plabel": prefered_label, "key": key}
        result_list.append(entry)
        line += 1

    return result_list


def process_presentation(reportnr: int, presentation: etree._Element) -> List[Dict[str, str]]:
    # first_key, loc_map = create_loc_map(presentation)
    # fill_parent_child(presentation, loc_map)
    entries = simple_list(presentation)
    if len(entries) > 0:
        first_tag = entries[0]['tag']
        stmt = None

        for k, v in stmt_map.items():
            if k in first_tag:
                stmt = v
        for entry in entries:
            entry['report'] = reportnr
            entry['stmt'] = stmt

    return entries


def process_presentations(root: etree._Element) -> List[Dict[str, str]]:
    presentation_links = list(root.iter('presentationLink'))
    print(len(presentation_links))
    report = 1
    all_entries:List[Dict[str, str]] = []
    for presentation in presentation_links:
        entries = process_presentation(report, presentation)
        all_entries.extend(entries)
        report += 1

    return all_entries


with open(file, "r", encoding="utf-8") as f:
    xml_content = f.read()
    data = _strip_file(xml_content)
    write_to_file(target_pre_clean_xml, data)
    root = etree.fromstring(data)
    entries = process_presentations(root)
    df = pd.DataFrame(entries)
    print(len(df))
