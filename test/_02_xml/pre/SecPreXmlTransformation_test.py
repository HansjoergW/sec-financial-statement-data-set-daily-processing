from _02_xml.pre._1_SecPreXmlExtracting import SecPreXmlExtractor
from _02_xml.pre._2_SecPreXmlTransformation import SecPreXmlTransformer

import os

scriptpath = os.path.realpath(__file__ + "/..")
data_folder = scriptpath + "/../data/"

testprexml = data_folder + "aapl-20200926_pre.xml"

def test_transform():
    extractor = SecPreXmlExtractor()
    transformer = SecPreXmlTransformer()
    with open(testprexml, "r", encoding="utf-8") as f:
        content: str = f.read()

        data = extractor.extract("", content)
        transformer.transform("", data)

        print(len(data))
        print(data)


def test_get_version_tag_name_from_href():
    testcases = [
        {"href":"http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_AccountingStandardsUpdate201802Member", "version":"us-gaap/2020", "tag":"AccountingStandardsUpdate201802Member"},
        {"href":"pki-20210103.xsd#pki_AccountingStandardsUpdate_201616Member", "version":"company", "tag":"AccountingStandardsUpdate_201616Member"},
    ]

    for testcase in testcases:
        details = SecPreXmlTransformer._get_version_tag_name_from_href(testcase['href'])

        assert details['tag'] == testcase['tag']
        assert details['version'] == testcase['version']