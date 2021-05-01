from _02_xml.SecXmlPreParsing import SecPreXmlParser
from _02_xml.SecXmlNumParsing import SecNumXmlParser
from lxml import etree

if __name__ == '__main__':


    with open('d:/secprocessing/xml/2021-04-24/gpox-20201031.xml', "r", encoding="utf-8") as f:
        content = f.read()

        parser = SecNumXmlParser()
        parser.parse(content)