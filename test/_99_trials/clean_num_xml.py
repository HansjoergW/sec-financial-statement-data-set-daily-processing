import re
from lxml import etree
import calendar
from typing import Dict, List, Tuple

file = "c:/ieu/projects/sec_processing/data/aapl-20200926_htm.xml"
target_num_clean_xml = "c:/ieu/projects/sec_processing/data/aapl-20200926_htm-clean.xml"

period_regex = re.compile(r"<period>|(</period>)", re.IGNORECASE + re.MULTILINE + re.DOTALL)
entity_regex = re.compile(r"(<entity>).*?(</entity>)", re.IGNORECASE + re.MULTILINE + re.DOTALL)
id_decimals_regex = re.compile(r"decimals[^>]*?id=\"[^<]*?\"", re.IGNORECASE + re.MULTILINE + re.DOTALL)
textblock_regex = re.compile(r"<[^/]*?TextBlock.*?<[/].*?TextBlock.*?>", re.IGNORECASE + re.MULTILINE + re.DOTALL)
xbrlns_regex = re.compile(r"xmlns=\".*?\"", re.IGNORECASE + re.MULTILINE + re.DOTALL)
link_regex = re.compile(r"<link.*?>", re.IGNORECASE + re.MULTILINE + re.DOTALL)
clean_tag_regex = re.compile(r"[{].*?[}]")

def strip_num_xml(pathtofile: str):
    with open(pathtofile, encoding="utf8") as f:
        data = f.read()
        data = entity_regex.sub("", data)
        data = period_regex.sub("", data)
        data = id_decimals_regex.sub("", data)
        data = textblock_regex.sub("", data)
        data = xbrlns_regex.sub("", data) # clear xbrlns, so it is easier to parse
        data = link_regex.sub("", data)

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

        id = context.get("id")
        print(id)
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

            context_map[id] = (enddate, qtrs)
        else:
            enddate = find_last_day_of_month(instanttxt)
            context_map[id] = (enddate, 0)

    return context_map


def parse_cleanfile(filename) -> Dict[str, Tuple[str]]:
    root = etree.parse(filename).getroot()
    us_gaap_ns = root.nsmap['us-gaap']
    pos = us_gaap_ns.rfind("/") + 1
    versionyear = us_gaap_ns[pos:pos+4]

    context_map = get_contexts(root)

    tags = list(root.findall('.//*[@unitRef]'))

    for tag in tags:
        value_text = tag.text
        ctxtRef = tag.get("contextRef")
        unitRef = tag.get("unitRef").lower()
        tagname = clean_tag_regex.sub("", tag.tag)
        version = tag.prefix + "/" + versionyear
        context_entry = context_map[ctxtRef]
        ddate = context_entry[0]
        qtrs = context_entry[1]

        if unitRef in ["usd","usdpershare"]:
            unitRef = "USD"


    print(len(tags))

    return context_map



#data = strip_num_xml(file)
#write_to_file(target_num_clean_xml, data)
contextMap = parse_cleanfile(target_num_clean_xml)

# print(find_last_day_of_month("2019-11-25"))
# print(find_last_day_of_month("2019-02-5"))
# print(find_last_day_of_month("2020-02-5"))
# print(find_last_day_of_month("2019-12-25"))

# print(qtrs("19", "09","20","09")) #4
# print(qtrs("19", "06","19","09")) #1
# print(qtrs("19", "10","20", "09")) #4
# print(qtrs("19", "08", "19", "10")) #1
