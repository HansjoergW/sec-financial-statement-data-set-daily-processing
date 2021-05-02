from _02_xml.SecXmlPreParsing import SecPreXmlParser
from _02_xml.SecXmlNumParsing import SecNumXmlParser
from lxml import etree

if __name__ == '__main__':

    file_ok = "d:/secprocessing/xml/2021-04-24/legx-20171231.xml"
    file_nok = "d:/secprocessing/xml/2021-04-24/duk-20201231_htm.xml"

    with open(file_nok, "r", encoding="utf-8") as f:
        content = f.read()

        parser = SecNumXmlParser()
        df = parser.parse(content)
        parser.clean_for_financial_statement_dataset(df, "accnr")
        print("")