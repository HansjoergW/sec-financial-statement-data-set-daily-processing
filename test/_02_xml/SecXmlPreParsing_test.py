from _02_xml.SecXmlPreParsing import SecPreXmlParser

from typing import Dict, List
from lxml import etree
import os

scriptpath = os.path.realpath(__file__ + "/..")

xml_test_data_file = scriptpath + '/data/test_pre.xml'
xml_expected_stripped_file = scriptpath + '/data/test_pre_exp.xml'
xml_unsorted_loc_file = scriptpath + '/data/test_pre_unsorted_loc.xml'
xml_complete_pre_file = scriptpath + "/data/aapl-20200926_pre.xml"


def test_strip_file():
    print(os.getcwd())
    print(scriptpath)

    with open(xml_test_data_file, "r", encoding="utf-8") as f:
        xml_content = f.read()
        f.close()

    parser = SecPreXmlParser()
    content = parser._strip_file(xml_content)

    with open(xml_expected_stripped_file, "r", encoding="utf-8") as f:
        xml_exp_content = f.read()
        f.close()

    assert content == xml_exp_content


def test_process_presentation():
    with open(xml_expected_stripped_file, "r", encoding="utf-8") as f:
        xml_exp_content = f.read()
    f.close()

    root = etree.fromstring(xml_exp_content)
    presentation_links = list(root.iter('presentationLink'))

    parser = SecPreXmlParser()
    data: List[Dict[str, str]] = parser._process_presentation(1, presentation_links[2])

    assert 7 == len(data)
    assert 8 == len(data[0])


def test_process_presentations():
    with open(xml_expected_stripped_file, "r", encoding="utf-8") as f:
        xml_exp_content = f.read()
    f.close()

    root = etree.fromstring(xml_exp_content)
    parser = SecPreXmlParser()
    df = parser._process_presentations(root, "H")

    assert 45 == len(df)
    assert 9 == len(df.columns)


def test_parse():
    with open(xml_expected_stripped_file, "r", encoding="utf-8") as f:
        xml_exp_content = f.read()
    f.close()

    parser = SecPreXmlParser()
    df = parser.parse(xml_exp_content)

    assert 45 == len(df)
    assert 9 == len(df.columns)


def test_clean_for_pure_pre():
    with open(xml_expected_stripped_file, "r", encoding="utf-8") as f:
        xml_exp_content = f.read()
    f.close()

    parser = SecPreXmlParser()
    df = parser.parse(xml_exp_content)
    df_clean = parser.clean_for_financial_statement_dataset(df, "an_adsh")

    assert 45 == len(df_clean)


def test_complete_file_parse():
    parser = SecPreXmlParser()

    with open(xml_complete_pre_file, "r", encoding="utf-8") as f:
        xml_content = f.read()
        df = parser.parse(xml_content)
        print(len(df))


def test_unsorted_loc_file_parse():
    with open(xml_unsorted_loc_file, "r", encoding="utf-8") as f:
        xml_exp_content = f.read()
    f.close()

    parser = SecPreXmlParser()
    df = parser.parse(xml_exp_content)
    df_clean = parser.clean_for_financial_statement_dataset(df, "an_adsh")

    assert len(df_clean[df_clean.index.isin(["IS"], level="stmt")]) > 0


def test_get_version_tag_name_from_href():
    testcases = [
        {"href":"http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_AccountingStandardsUpdate201802Member", "version":"us-gaap/2020", "tag":"AccountingStandardsUpdate201802Member"},
        {"href":"pki-20210103.xsd#pki_AccountingStandardsUpdate_201616Member", "version":"company", "tag":"AccountingStandardsUpdate_201616Member"},
    ]

    for testcase in testcases:
        details = SecPreXmlParser._get_version_tag_name_from_href(testcase['href'])

        assert details['tag'] == testcase['tag']
        assert details['version'] == testcase['version']
