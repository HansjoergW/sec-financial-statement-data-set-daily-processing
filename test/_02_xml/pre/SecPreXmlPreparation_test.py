from _02_xml.pre.SecPreXmlExtracting import SecPreXmlExtractor

from typing import List, Dict, Tuple
import os

scriptpath = os.path.realpath(__file__ + "/..")
data_folder = scriptpath + "/../data/"

testprexml = data_folder + "aapl-20200926_pre.xml"

def test_read():
    preparer = SecPreXmlExtractor()
    with open(testprexml, "r", encoding="utf-8") as f:
        content: str = f.read()
        data: Dict[int,Tuple[str, List[Dict[str,str]], List[Dict[str, str]]]] = preparer.preparexml(content)
        print(len(data))
        print(data)
