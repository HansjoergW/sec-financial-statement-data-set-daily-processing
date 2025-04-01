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

    df_clean, fye = parser.clean_for_financial_statement_dataset(df, "")
    assert fye == '0926'
    assert 578 == len(df_clean)
    assert 4 == len(df_clean.columns)









