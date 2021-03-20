from _02_xml.SecPreXmlParsing import SecPreXmlParser

from typing import Dict, List, Tuple, Optional
from lxml import etree
import os

xml_test_data_file = './data/test_pre.xml'

xml_expected_stripped_file = './data/test_pre_exp.xml'


def test_strip_file():
    print(os.getcwd())
    with open(xml_test_data_file, "r", encoding="utf-8") as f:
        xml_content = f.read()
        f.close()

    parser = SecPreXmlParser()
    content = parser._strip_file(xml_content)

    with open(xml_expected_stripped_file, "r", encoding="utf-8") as f:
        xml_exp_content = f.read()
        f.close()

    assert content == xml_exp_content


def test_get_prefered_label():
    with open(xml_expected_stripped_file, "r", encoding="utf-8") as f:
        xml_exp_content = f.read()
        f.close()

    root = etree.fromstring(xml_exp_content)

    parser = SecPreXmlParser()
    data: Dict[str, str] = parser._get_prefered_label(root)

    assert 45 == len(data)


def test_simple_list():
    with open(xml_expected_stripped_file, "r", encoding="utf-8") as f:
        xml_exp_content = f.read()
        f.close()

    root = etree.fromstring(xml_exp_content)

    parser = SecPreXmlParser()
    data: List[Dict[str, str]] = parser._simple_list(root)

    assert 52 == len(data)
    assert 6 == len(data[0])


def test_process_presentation():
    with open(xml_expected_stripped_file, "r", encoding="utf-8") as f:
        xml_exp_content = f.read()
    f.close()

    root = etree.fromstring(xml_exp_content)
    presentation_links = list(root.iter('presentationLink'))

    parser = SecPreXmlParser()
    data: List[Dict[str, str]] = parser._process_presentation(1, presentation_links[2])

    assert 8 == len(data)
    assert 9 == len(data[0])


def test_process_presentations():
    with open(xml_expected_stripped_file, "r", encoding="utf-8") as f:
        xml_exp_content = f.read()
    f.close()

    root = etree.fromstring(xml_exp_content)
    parser = SecPreXmlParser()
    df = parser._process_presentations(root, "H")

    assert 52 == len(df)
    assert 10 == len(df.columns)


def test_parse():
    with open(xml_expected_stripped_file, "r", encoding="utf-8") as f:
        xml_exp_content = f.read()
    f.close()

    parser = SecPreXmlParser()
    df = parser.parse(xml_exp_content, "H")

    assert 52 == len(df)
    assert 10 == len(df.columns)


def test_clean_for_pure_pre():
    with open(xml_expected_stripped_file, "r", encoding="utf-8") as f:
        xml_exp_content = f.read()
    f.close()

    parser = SecPreXmlParser()
    df = parser.parse(xml_exp_content, "H")
    df_clean = parser.clean_for_pure_pre(df, "an_adsh")

    assert 52 == len(df_clean)


def test_complete_file_parse():
    xml_file = "c:/ieu/projects/sec_processing/data/aapl-20200926_pre.xml"
    parser = SecPreXmlParser()

    with open(xml_file, "r", encoding="utf-8") as f:
        xml_content = f.read()
        df = parser.parse(xml_content, "H")
        print(len(df))