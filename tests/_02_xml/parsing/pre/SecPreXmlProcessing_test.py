from _02_xml.parsing.pre._1_SecPreXmlExtracting import SecPreXmlExtractor
from _02_xml.parsing.pre._2_SecPreXmlTransformation import SecPreXmlTransformer
from _02_xml.parsing.pre._3_SecPreXmlGroupTransformation import  SecPreXmlGroupTransformer
from _02_xml.parsing.pre._4_SecPreXmlProcessing import SecPreXmlDataProcessor

import os

scriptpath = os.path.realpath(__file__ + "/../..")
data_folder = scriptpath + "/../data/"

testprexml_norm = data_folder + "aapl-20200926_pre.xml"
testprexml_numbered_label = data_folder + "0000016160-21-000018-calm-20210227_pre.xml"

extractor = SecPreXmlExtractor()
transformer = SecPreXmlTransformer()
grouptransformer = SecPreXmlGroupTransformer()
processor = SecPreXmlDataProcessor()


def test_process():
    with open(testprexml_numbered_label, "r", encoding="utf-8") as f:
        content: str = f.read()

        data = extractor.extract("", content)
        data_transformed= transformer.transform("", data)
        data_grouptransformed= grouptransformer.grouptransform("", data_transformed)
        data_processed = processor.process("", data_grouptransformed)

        print(len(data_processed))