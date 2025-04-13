import os

from secdaily._02_xml.parsing.SecXmlPreParsing import SecPreXmlParser

scriptpath = os.path.realpath(__file__ + "/../..")

xml_test_data_file = scriptpath + "/data/test_pre.xml"
xml_expected_stripped_file = scriptpath + "/data/test_pre_exp.xml"
xml_unsorted_loc_file = scriptpath + "/data/test_pre_unsorted_loc.xml"
xml_complete_pre_file = scriptpath + "/data/aapl-20200926_pre.xml"


def test_parse():
    with open(xml_expected_stripped_file, "r", encoding="utf-8") as f:
        xml_exp_content = f.read()
    f.close()

    parser = SecPreXmlParser()
    df, errorlist = parser.parse("", xml_exp_content)

    assert 45 == len(df)
    assert 9 == len(df.columns)


def test_clean_for_pure_pre():
    with open(xml_expected_stripped_file, "r", encoding="utf-8") as f:
        xml_exp_content = f.read()
    f.close()

    parser = SecPreXmlParser()
    df, _ = parser.parse("", xml_exp_content)
    assert 45 == len(df)


def test_complete_file_parse():
    parser = SecPreXmlParser()

    with open(xml_complete_pre_file, "r", encoding="utf-8") as f:
        xml_content = f.read()
        df, _ = parser.parse("", xml_content)
        print(len(df))


def test_unsorted_loc_file_parse():
    with open(xml_unsorted_loc_file, "r", encoding="utf-8") as f:
        xml_exp_content = f.read()
    f.close()

    parser = SecPreXmlParser()
    df, _ = parser.parse("", xml_exp_content)

    assert len(df) == 27
    assert len(df[df.stmt == "IS"]) == 27
