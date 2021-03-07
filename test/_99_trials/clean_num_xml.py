import re

file = "c:/ieu/projects/sec_processing/data/aapl-20200926_htm.xml"
target_num_clean_xml = "c:/ieu/projects/sec_processing/data/aapl-20200926_htm-clean.xml"

entity_regex = re.compile(r"(<entity>).*?(</entity>)", re.IGNORECASE + re.MULTILINE + re.DOTALL)
entity_regex = re.compile(r"(<entity>).*?(</entity>)", re.IGNORECASE + re.MULTILINE + re.DOTALL)
id_decimals_regex = re.compile(r"decimals[^>]*?id=\"[^<]*?\"", re.IGNORECASE + re.MULTILINE + re.DOTALL)
textblock = re.compile(r"<[^/]*?TextBlock.*?<[/].*?TextBlock.*?>", re.IGNORECASE + re.MULTILINE + re.DOTALL)

def strip_num_xml(pathtofile: str):
    with open(pathtofile, encoding="utf8") as f:
        data = f.read()

        data = entity_regex.sub("", data)
        data = id_decimals_regex.sub("", data)
        data = textblock.sub("", data)

    return data


def write_to_file(filename, data):
    with open(filename, "w", encoding="utf8") as f:
        f.write(data)
        f.close()


data = strip_num_xml(file)
write_to_file(target_num_clean_xml, data)
