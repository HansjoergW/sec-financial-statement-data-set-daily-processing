from _02_xml.SecXmlPreParsing import SecPreXmlParser
from _02_xml.SecXmlNumParsing import SecNumXmlParser
from lxml import etree

#special cases
# default namespace  xmlns="http://www.xbrl.org/2003/linkbase": d:/secprocessing/xml/2021-05-02/vgz-20210331_pre.xml

if __name__ == '__main__':

    file_ok = "d:/secprocessing/xml/2021-04-24/blpg-20200630_pre.xml"
    file_nok = "d:/secprocessing/xml/2021-05-02/vgz-20210331_pre.xml"
    file_empty= "d:/secprocessing/xml/2021-05-06/nvec-20210331_pre.xml"
    file_oder = "d:/secprocessing/xml/2021-04-24/uboh-20201231_pre.xml"

    with open(file_oder, "r", encoding="utf-8") as f:
        content = f.read()

        parser = SecPreXmlParser()
        df = parser.parse(content)
        df_clean = parser.clean_for_financial_statement_dataset(df, "accnr")
        print(df_clean.shape) # die meisten attribute sind im index, daher ist die anzahl der spalten nur 3