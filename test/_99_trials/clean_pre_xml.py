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
role_regex = re.compile(r"http://www.xbrl.org/2003/role/", re.IGNORECASE + re.MULTILINE + re.DOTALL)
href_regex = re.compile(" href=\".*?#", re.IGNORECASE + re.MULTILINE + re.DOTALL)
type_clean_regex = re.compile("( type=\"locator\")|( type=\"arc\")", re.IGNORECASE + re.MULTILINE + re.DOTALL)
arcrole_parent_child_regex = re.compile(" arcrole=\"parent-child\"", re.IGNORECASE + re.MULTILINE + re.DOTALL)

def _strip_file(data: str) -> str:
    """removes unneeded content from the datastring, so that xml file is easier to understand and xml parsing will be faster"""
    data = remove_unicode_tag_regex.sub("", data)
    data = link_regex.sub("<", data)
    data = link_end_regex.sub("</", data)
    data = xlink_regex.sub(" ", data)
    data = arcrole_regex.sub("", data)
    data = role_regex.sub("", data)
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


def simple_list(presentation: etree._Element) -> List[Dict[str, str]]:
    locs  = list(presentation.iter('loc'))
    result_list = []
    line = 0
    for loc in locs:
        key = loc.get("label")
        tag_info = loc.get("href").split("_")
        tag_prefix = tag_info[0]
        tag = tag_info[1]
        entry = {"line": line, "version": tag_prefix, "tag": tag, "key": key}
        result_list.append(entry)
        line += 1

    return result_list

# CP CoverPage, EQ Equity, IS IncomeStatement, CI ComprehensiveIncome, BS BalanceSheet, CF CashFlow

def process_presentation(presentation: etree._Element):
    # first_key, loc_map = create_loc_map(presentation)
    # fill_parent_child(presentation, loc_map)
    entries = simple_list(presentation)
    if len(entries) > 0:
        print(entries[0]['tag'])
    else:
        print("---")


def find_presentation_links(root: etree._Element):
    presentation_links = list(root.iter('presentationLink'))
    print(len(presentation_links))

    for presentation in presentation_links:
        process_presentation(presentation)


with open(file, "r", encoding="utf-8") as f:
    xml_content = f.read()
    data = _strip_file(xml_content)
    write_to_file(target_pre_clean_xml, data)
    root = etree.fromstring(data)
    find_presentation_links(root)
