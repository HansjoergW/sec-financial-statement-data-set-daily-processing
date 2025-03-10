from secdaily._02_xml.parsing.pre._1_SecPreXmlExtracting import SecPreXmlExtractor, SecPreExtractPresentationLink

from typing import List, Dict, Tuple, Union
import os

scriptpath = os.path.realpath(__file__ + "/../..")
data_folder = scriptpath + "/../data/"

xml_test_data_file = data_folder + 'test_pre.xml'
xml_expected_stripped_file = data_folder + 'test_pre_exp.xml'

testprexml = data_folder + "aapl-20200926_pre.xml"

def test_read():
    preparer = SecPreXmlExtractor()
    with open(testprexml, "r", encoding="utf-8") as f:
        content: str = f.read()
        data: Dict[int, SecPreExtractPresentationLink] = preparer.extract("", content)
        print(len(data))
        print(data)


def test_strip_file():

    with open(xml_test_data_file, "r", encoding="utf-8") as f:
        xml_content = f.read()
        f.close()

    parser = SecPreXmlExtractor()
    content = parser._strip_file(xml_content)

    with open(xml_expected_stripped_file, "r", encoding="utf-8") as f:
        xml_exp_content = f.read()
        f.close()

    assert content == xml_exp_content