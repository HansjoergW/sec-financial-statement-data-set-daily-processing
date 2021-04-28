from _02_xml.SecXmlNumParsing import SecNumXmlParser

if __name__ == '__main__':

    urg failed..

    with open('c:/tmp/cday-10k_20201231_htm.xml', "r", encoding="utf-8") as f:
        content = f.read()

        parser = SecNumXmlParser()
        parser.parse(content)