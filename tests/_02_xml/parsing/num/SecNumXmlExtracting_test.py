import os
from typing import List

from lxml import etree, objectify
from secdaily._02_xml.parsing.num._1_SecNumXmlExtracting import SecNumExtraction, SecNumXmlExtractor

scriptpath = os.path.realpath(__file__ + "/../..")
data_folder = scriptpath + "/../data/"

xml_test_data_file = data_folder + 'test_num.xml'
xml_expected_stripped_file = data_folder + 'test_num_exp.xml'

testnumxml = data_folder + "aapl-20200926_htm.xml"


def test_read():
    preparer = SecNumXmlExtractor()
    with open(testnumxml, "r", encoding="utf-8") as f:
        content: str = f.read()
        data: SecNumExtraction = preparer.extract("", content)

        assert len(data.contexts) == 318
        assert len(data.tags) == 1236


def test_strip_file():

    with open(xml_test_data_file, "r", encoding="utf-8") as f:
        xml_content = f.read()
        f.close()

    parser = SecNumXmlExtractor()
    content = parser._strip_file(xml_content)

    with open(xml_expected_stripped_file, "r", encoding="utf-8") as f:
        xml_exp_content = f.read()
        f.close()

    result = objectify.fromstring(content)
    expected = objectify.fromstring(xml_exp_content)

    result_str = etree.tostring(result)
    expected_str = etree.tostring(expected)

    assert result_str == expected_str


def test_find_company_namespaces():
    with open(xml_expected_stripped_file, "r", encoding="utf-8") as f:
        xml_exp_content = f.read()
    f.close()

    parser = SecNumXmlExtractor()
    root = etree.fromstring(xml_exp_content)
    company_namespaces = parser._find_company_namespaces(root)

    assert len(company_namespaces) == 1
    assert company_namespaces[0] == 'aapl'


def test_read_contexts():
    with open(xml_expected_stripped_file, "r", encoding="utf-8") as f:
        xml_exp_content = f.read()
    f.close()

    parser = SecNumXmlExtractor()
    root = etree.fromstring(xml_exp_content)

    content:List = parser._read_contexts(root)
    assert len(content) == 3
