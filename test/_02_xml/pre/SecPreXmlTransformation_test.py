from _02_xml.pre.SecPreXmlExtracting import SecPreXmlExtractor
from _02_xml.pre.SecPreXmlTransformation import SecPreXmlTransformer

from typing import List, Dict, Union
import os

scriptpath = os.path.realpath(__file__ + "/..")
data_folder = scriptpath + "/../data/"

testprexml = data_folder + "aapl-20200926_pre.xml"

def test_transform():
    preparer = SecPreXmlExtractor()
    transformer = SecPreXmlTransformer()
    with open(testprexml, "r", encoding="utf-8") as f:
        content: str = f.read()

        data: Dict[int,Dict[str, Union[str, List[Dict[str, str]]]]] = preparer.preparexml(content)
        transformer.transform(data)

        print(len(data))
        print(data)

