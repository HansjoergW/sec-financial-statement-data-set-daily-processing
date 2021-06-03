from _02_xml.pre._1_SecPreXmlExtracting import SecPreXmlExtractor
from _02_xml.pre.SecPreXmlTransformation import SecPreXmlTransformer
from _02_xml.pre.SecPreXmlProcessing import SecPreXmlDataProcessor


from typing import List, Dict, Union
import os

scriptpath = os.path.realpath(__file__ + "/..")
data_folder = scriptpath + "/../data/"

testprexml_norm = data_folder + "aapl-20200926_pre.xml"
testprexml_numbered_label = data_folder + "0000016160-21-000018-calm-20210227_pre.xml"

extractor = SecPreXmlExtractor()
transformer = SecPreXmlTransformer()
processor = SecPreXmlDataProcessor()


def test_process():
    with open(testprexml_numbered_label, "r", encoding="utf-8") as f:
        content: str = f.read()

        data: Dict[int,Dict[str, Union[str, List[Dict[str, str]]]]] = extractor.extract("", content)
        data_transformed: Dict[int,Dict[str, Union[str, List[Dict[str, str]]]]] = transformer.transform("", data)
        data_processed = processor.process("", data_transformed)

        print(len(data_processed))