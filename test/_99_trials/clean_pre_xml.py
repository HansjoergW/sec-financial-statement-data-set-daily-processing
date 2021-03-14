import re
from lxml import etree
import calendar
import pandas as pd
from typing import Dict, List, Tuple

file = "c:/ieu/projects/sec_processing/data/aapl-20200926_pre.xml"
target_num_clean_xml = "c:/ieu/projects/sec_processing/data/aapl-20200926_pre-clean.xml"

period_regex = re.compile(r"<period>|(</period>)", re.IGNORECASE + re.MULTILINE + re.DOTALL)
entity_regex = re.compile(r"<entity>|(</entity>)", re.IGNORECASE + re.MULTILINE + re.DOTALL)
identifier_regex = re.compile(r"(<identifier).*?(</identifier>)", re.IGNORECASE + re.MULTILINE + re.DOTALL)
id_decimals_regex = re.compile(r"decimals[^>]*?id=\"[^<]*?\"", re.IGNORECASE + re.MULTILINE + re.DOTALL)
textblock_regex = re.compile(r"<[^/]*?TextBlock.*?<[/].*?TextBlock.*?>", re.IGNORECASE + re.MULTILINE + re.DOTALL)
xbrlns_regex = re.compile(r"xmlns=\".*?\"", re.IGNORECASE + re.MULTILINE + re.DOTALL)
link_regex = re.compile(r"<link.*?>", re.IGNORECASE + re.MULTILINE + re.DOTALL)
clean_tag_regex = re.compile(r"[{].*?[}]")
remove_wspace_regex = re.compile(r">[\s\r\n]*<", re.IGNORECASE + re.MULTILINE + re.DOTALL)

def strip_num_xml(pathtofile: str):
    with open(pathtofile, encoding="utf8") as f:
        data = f.read()
        data = identifier_regex.sub("", data)
        data = period_regex.sub("", data)
        data = entity_regex.sub("", data)
        data = id_decimals_regex.sub("", data)
        data = textblock_regex.sub("", data)
        data = xbrlns_regex.sub("", data) # clear xbrlns, so it is easier to parse
        data = link_regex.sub("", data)
        data = remove_wspace_regex.sub("><", data)

    return data


def write_to_file(filename, data):
    with open(filename, "w", encoding="utf8") as f:
        f.write(data)
        f.close()


def find_last_day_of_month(datastr:str) -> str:
    yearstr  = datastr[0:4]
    monthstr = datastr[5:7]
    daystr = datastr[8:]

    year = int(yearstr)
    month = int(monthstr)

    last_day_of_month = calendar.monthrange(year, month)[1]
    return yearstr + monthstr + str(last_day_of_month).zfill(2)


def calculate_qtrs(year_start_s: str, month_start_s: str, year_end_s: str, month_end_s: str) -> int:
    year_start = int(year_start_s)
    year_end = int(year_end_s)
    month_start = int(month_start_s)
    month_end = int(month_end_s) + (year_end - year_start) * 12


    return int(round(float(month_end - month_start) / 3))



def get_contexts(root: etree._Element):
    contexts = list(root.iter('context'))
    context_map: Dict[str, Tuple[str]] = {}
    for context in contexts:
        instanttxt = None
        startdatetxt = None
        enddatetxt = None

        segments = list(context.findall('.//*[@dimension]'))
        segments_list = []
        for segment in segments:
            segment_label = segment.text
            segment_dim = segment.get("dimension")
            segments_list.append(segment_dim + "/" + segment_label)

        if len(segments_list) == 0:
            segments_list = None

        id = context.get("id")
        instant = context.find('instant')
        if instant is not None:
            instanttxt = instant.text

        startdate = context.find('startDate')
        if startdate is not None:
            startdatetxt = startdate.text

        enddate = context.find('endDate')
        if enddate is not None:
            enddatetxt = enddate.text

        if instant is None:
            enddate = find_last_day_of_month(enddatetxt)
            qtrs = calculate_qtrs(startdatetxt[0:4], startdatetxt[5:7], enddatetxt[0:4], enddatetxt[5:7])

            context_map[id] = (enddate, qtrs, segments_list)
        else:
            enddate = find_last_day_of_month(instanttxt)
            context_map[id] = (enddate, 0, segments_list)

    return context_map


def parse_cleanfile(filename) -> pd.DataFrame:
    root = etree.parse(filename).getroot()

    us_gaap_ns = root.nsmap['us-gaap']
    pos = us_gaap_ns.rfind("/") + 1
    versionyear = us_gaap_ns[pos:pos+4]

    context_map = get_contexts(root)

    tags = list(root.findall('.//*[@unitRef]'))

    entries = []

    for tag in tags:
        temp_dict = {}

        value_text = tag.text
        ctxtRef = tag.get("contextRef")
        unitRef = tag.get("unitRef").lower()
        tagname = clean_tag_regex.sub("", tag.tag)
        version = tag.prefix + "/" + versionyear
        context_entry = context_map[ctxtRef]
        ddate = context_entry[0]
        qtrs = context_entry[1]
        segments = context_entry[2]

        if unitRef in ["usd","usdpershare"]:
            unitRef = "USD"

        temp_dict['adsh']    = ''
        temp_dict['tag']     = tagname
        temp_dict['version'] = version
        temp_dict['coreg']   = ''
        temp_dict['ddate']   = ddate
        temp_dict['qtrs']    = qtrs
        temp_dict['uom']     = unitRef
        temp_dict['value']   = value_text
        temp_dict['footnote'] = ''
        temp_dict['segments'] = segments

        entries.append(temp_dict)

    return pd.DataFrame(entries)


data = strip_num_xml(file)
write_to_file(target_num_clean_xml, data)
#content = parse_cleanfile(target_num_clean_xml)
#print(len(content))
#print(sum(~content['segments'].isnull()))

# print(find_last_day_of_month("2019-11-25"))
# print(find_last_day_of_month("2019-02-5"))
# print(find_last_day_of_month("2020-02-5"))
# print(find_last_day_of_month("2019-12-25"))

# print(qtrs("19", "09","20","09")) #4
# print(qtrs("19", "06","19","09")) #1
# print(qtrs("19", "10","20", "09")) #4
# print(qtrs("19", "08", "19", "10")) #1

# Problem: es sind mehrere Werte für das gleiche Tag und das gleiche Datum vorhanden
# z.B. CostofGoodsAndServicesSold -> im XML 9 Einträge, im CSV nur 3
# Grund:
# der Context hat manchmal auch ein oder mehrere Segmente:
# <segment>
# <xbrldi:explicitMember dimension="srt:ProductOrServiceAxis">us-gaap:ProductMember</xbrldi:explicitMember>
# </segment>
#
# und die Dimension und quasi den TextInhalt sollte man mitnehmen
# -> das ermöglicht zusätzliche Aufteilung.
# die Zahlen, die in erster Linie interessieren, sind diejenigen ohne segment FileNotFoundError
