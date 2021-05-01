from _02_xml.SecXmlPreParsing import SecPreXmlParser
from _02_xml.SecXmlNumParsing import SecNumXmlParser
from lxml import etree

if __name__ == '__main__':


    with open('d:/secprocessing/xml/2021-04-24/zivo-20201231.xml', "r", encoding="utf-8") as f:
        content = f.read()

        parser = SecNumXmlParser()
        df = parser.parse(content)
        print("")