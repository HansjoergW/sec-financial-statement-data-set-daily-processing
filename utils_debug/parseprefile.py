from _02_xml.SecXmlPreParsing import SecPreXmlParser
from _02_xml.SecXmlNumParsing import SecNumXmlParser
from lxml import etree

if __name__ == '__main__':

    file_ok = "d:/secprocessing/xml/2021-04-24/blpg-20200630_pre.xml"
    file_nok = "d:/secprocessing/xml/2021-04-24/cspi-20200930_pre.xml"

    with open(file_nok, "r", encoding="utf-8") as f:
        content = f.read()

        parser = SecPreXmlParser()
        df = parser.parse(content)
        df_clean = parser.clean_for_financial_statement_dataset(df, "accnr")
        print("")