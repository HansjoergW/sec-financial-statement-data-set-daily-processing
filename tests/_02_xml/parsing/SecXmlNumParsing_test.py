from secdaily._02_xml.parsing.SecXmlNumParsing import SecNumXmlParser

from typing import Dict, Tuple, Optional
from lxml import etree, objectify
import os

scriptpath = os.path.realpath(__file__ + "/../..")
data_folder = scriptpath + "/data/"


testnumxml = data_folder + "aapl-20200926_htm.xml"

def test_parse():
    with open(testnumxml, "r", encoding="utf-8") as f:
        xml_exp_content = f.read()
    f.close()

    parser = SecNumXmlParser()
    df, errorlist = parser.parse("", xml_exp_content)

    assert 1223 == len(df)
    assert 12 == len(df.columns)
    assert 0 == len(errorlist)

    df_clean = parser.clean_for_financial_statement_dataset(df, "")
    assert 565 == len(df_clean)
    assert 3 == len(df_clean.columns)









