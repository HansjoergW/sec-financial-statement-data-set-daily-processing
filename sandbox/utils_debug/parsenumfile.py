from secdaily._02_xml.parsing.SecXmlNumParsing import SecNumXmlParser
from secdaily._00_common.DebugUtils import DataAccessByAdshTool

workdir = "d:/secprocessing/"

xml_content = """
"""

def get_num_xml_content_by_adsh(adsh: str)-> str :
    by_adsh = DataAccessByAdshTool(workdir, adsh, 2021, 1)
    return by_adsh.get_num_xml_content()


def get_num_xml_content_from_file(file: str)-> str:
    with open(file, "r", encoding="utf-8") as f:
        return f.read()


def parse_content(adsh, content:  str):
    parser = SecNumXmlParser()
    (df, errors) = parser.parse(adsh, content)
    df_clean = parser.clean_for_financial_statement_dataset(df, adsh)
    print(df_clean.shape)


if __name__ == '__main__':
    #adsh = "0000107140-20-000068" # working für trading, stocks
    #adsh = "0001213900-21-014067" # failing for trading, stock
    adsh = "0001126234-21-000034" # None-Type not ssubscriptable
    content = get_num_xml_content_by_adsh(adsh)
    #content = xml_content
    parse_content(adsh, content)