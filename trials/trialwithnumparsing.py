from _02_xml.SecXmlPreParsing import SecPreXmlParser
from lxml import etree

if __name__ == '__main__':


    with open('/testdata/cday-20201231_pre.xml', "r", encoding="utf-8") as f:
        content = f.read()
        content = bytes(bytearray(content, encoding='utf-8'))

        #parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')
        etree.fromstring(content) #, parser=parser)

        parser = SecPreXmlParser()
        parser.parse(content)