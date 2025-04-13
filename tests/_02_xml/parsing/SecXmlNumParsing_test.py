import os

from secdaily._02_xml.parsing.SecXmlNumParsing import SecNumXmlParser

scriptpath = os.path.realpath(__file__ + "/../..")
data_folder = scriptpath + "/data/"


testnumxml = data_folder + "aapl-20200926_htm.xml"

def test_parse():
    with open(testnumxml, "r", encoding="utf-8") as f:
        xml_exp_content = f.read()
    f.close()

    parser = SecNumXmlParser()
    df, errorlist = parser.parse("", xml_exp_content)

    assert 1236 == len(df)
    assert 12 == len(df.columns)
    assert 0 == len(errorlist)
