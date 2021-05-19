from _00_common.DebugUtils import DataAccessTool, TestSetCreatorTool
from _00_common.DBManagement import DBManager
from _02_xml.pre.SecPreXmlExtracting import SecPreXmlExtractor
from _02_xml.pre.SecPreXmlTransformation import SecPreXmlTransformer
from _02_xml.pre.SecPreXmlProcessing import SecPreXmlDataProcessor

from typing import List, Dict, Tuple
from multiprocessing import Pool
import logging


""" Idee::
hier irgendwie die einzelnen Tests als Klassen ablegen.
zB. prüfen ob Anzahl Reports identisch, Total und pro Typ -> das erste, was wir sicherstellen möchten.

Die einzelnen TestAspekte müssen separiert werden, sonst gibt es ein durcheinander

"""

default_workdir = "d:/secprocessing"
testsetcreator = TestSetCreatorTool(default_workdir)
dbmgr = DBManager(default_workdir)


def prepare_func(data: Tuple[str, str]) -> str:
    pre_xml_preparer = SecPreXmlExtractor()
    pre_xml_transformer = SecPreXmlTransformer()
    pre_xml_processor = SecPreXmlDataProcessor()

    adsh = data[0]
    pre_xml_file = data[1]
    try:
        with open(pre_xml_file, "r", encoding="utf-8") as f:
            content: str = f.read()
            extracted_data = pre_xml_preparer.extract(adsh, content)
            transformed_data = pre_xml_transformer.transform(adsh, extracted_data)
            processed_data = pre_xml_processor.process(adsh, transformed_data)
            return None
    except Exception as e:
        return adsh + " - " + pre_xml_file + " - " + str(e)



def test_preXmlParsing():
    logging.basicConfig(level=logging.INFO)
    # complete run needs about 4 minutes
    # executes the complete parsing on all of the available reports from the
    # provided year and months
    adshs: List[str] = testsetcreator.get_testset_by_year_and_months(2021, [1,2,3])
    xml_files_info: List[Tuple[str, str, str]] = dbmgr.get_xml_files_info_from_sec_processing_by_adshs(adshs)
    pre_xml_files_info: List[Tuple[str, str]] = [(x[0], x[2]) for x in xml_files_info] # adsh and preXmlFile

    pool = Pool(8)

    all_failed = []
    print("adsh to test: ", len(adshs))
    for i in range(0, len(pre_xml_files_info), 500):
        chunk = pre_xml_files_info[i:i + 500]
        failed: List[str] = pool.map(prepare_func, chunk)
        print(".", end="")
        failed = [x for x in failed if x is not None]
        all_failed.extend(failed)

    for failed in all_failed:
        print(failed)

if __name__ == '__main__':
    test_preXmlParsing()