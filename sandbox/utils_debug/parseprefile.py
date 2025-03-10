from secdaily._02_xml.SecXmlPreParsing import SecPreXmlParser
from secdaily._00_common.DebugUtils import DataAccessByAdshTool

"""
Helper Class to process a single report based on the ADSH Nummer or directly from an xml content 
"""


workdir = "d:/secprocessing/"

xml_content = """
"""


def get_pre_xml_content_by_adsh(adsh: str)-> str :
    by_adsh = DataAccessByAdshTool(workdir, adsh, 2021, 1)
    return by_adsh.get_pre_xml_content()


def get_pre_xml_content_from_file(file: str)-> str:
    with open(file, "r", encoding="utf-8") as f:
        return f.read()


def parse_content(adsh, content:  str):
    parser = SecPreXmlParser()
    (df, errors) = parser.parse(adsh, content)
    df_clean = parser.clean_for_financial_statement_dataset(df, adsh)
    print(df_clean.shape) # die meisten attribute sind im index, daher ist die anzahl der spalten nur 3


if __name__ == '__main__':
    # adsh = "0001213900-21-009521" # IS Sonderfall
    # adsh = "0001213900-21-012572" # sonderfall IS ConsolidatedBalanceSheet0 / ConsolidatedBalanceSheet_Parentheticals0->
    # adsh = "0001193125-21-081336" # IS Sonderfall in Liquidation
    # adsh = "0001140361-21-004772" # IS Sonderfall in Liquidation
    # adsh = "0001193125-21-040108" # IS Sonderfall in Liquidation

    # adsh = "0000070866-21-000011" # CI inpth in Zip as BS
    # adsh = "0000074260-21-000021" # CF inpth in Zip as CI
    # adsh = "0001254699-21-000005" # CF   missing wegen multiple root nodes
    # adsh = "0001628280-21-002278" # CF   missing wegen multiple root nodes


    # adsh = ""
    # adsh = "" # missing IS

    # adsh = "0000007789-21-000018"
    #adsh = "0001564590-21-008444"

    content = get_pre_xml_content_by_adsh(adsh)
    #content = xml_content
    parse_content(adsh, content)


# old special cases

"""
   
"""

