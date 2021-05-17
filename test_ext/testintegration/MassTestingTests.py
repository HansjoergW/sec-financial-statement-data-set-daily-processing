from _00_common.DebugUtils import DataAccessTool, TestSetCreatorTool
from _00_common.DBManagement import DBManager
from _02_xml.pre.SecPreXmlExtracting import SecPreXmlExtractor

from typing import List, Dict, Tuple
from multiprocessing import Pool


""" Idee::
hier irgendwie die einzelnen Tests als Klassen ablegen.
zB. prüfen ob Anzahl Reports identisch, Total und pro Typ -> das erste, was wir sicherstellen möchten.

Die einzelnen TestAspekte müssen separiert werden, sonst gibt es ein durcheinander

"""

default_workdir = "d:/secprocessing"
testsetcreator = TestSetCreatorTool(default_workdir)
dbmgr = DBManager(default_workdir)


def prepare_func(data: Tuple[str, str]):
    pre_xml_preparer = SecPreXmlExtractor()
    adsh = data[0]
    pre_xml_file = data[1]
    with open(pre_xml_file, "r", encoding="utf-8") as f:
        content: str = f.read()
        pre_xml_preparer.preparexml(content)


def test_preXmlPreparer():
    # complete run needs about 100seconds
    adshs: List[str] = testsetcreator.get_testset_by_year_and_months(2021, [1,2,3])
    xml_files_info: List[Tuple[str, str, str]] = dbmgr.get_xml_files_info_from_sec_processing_by_adshs(adshs)
    pre_xml_files_info: List[Tuple[str, str]] = [(x[0], x[2]) for x in xml_files_info] # adsh and preXmlFile

    pool = Pool(8)

    for i in range(0, len(pre_xml_files_info), 500):
        chunk = pre_xml_files_info[i:i + 500]
        pool.map(prepare_func, chunk)
        print(".", end="")


if __name__ == '__main__':
    test_preXmlPreparer()