from _02_xml.SecXmlNumParsing import SecNumXmlParser
from _00_common.DebugUtils import DataAccessByAdshTool

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
    adsh = "0000004904-21-000010" # data mit coreg Infos AccountsPayableCurrent  z.B. SouthwesternElectricPowerCo
    content = get_num_xml_content_by_adsh(adsh)
    #content = xml_content
    parse_content(adsh, content)