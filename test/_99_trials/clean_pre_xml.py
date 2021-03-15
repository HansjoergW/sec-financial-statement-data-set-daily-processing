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


def find_presentation_links(root: etree._Element):
    presentation_links = list(root.iter('presentationLink'))
    print(len(presentation_links))


with open(file, "r", encoding="utf-8") as f:
    xml_content = f.read()
    data = _strip_file(xml_content)
    write_to_file(target_pre_clean_xml, data)
    root = etree.fromstring(data)
    find_presentation_links(root)
