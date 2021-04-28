from _00_common.DBManagement import DBManager
from _02_xml.SecXmlFileProcessing import SecXmlFileProcessor
from _02_xml.SecXmlFileParsing import SecXmlParser
import shutil
import pytest

folder = "./tmp"

@pytest.fixture(scope="module")
def dbmgr():
    shutil.rmtree(folder, ignore_errors=True)
    new_dbmgr = DBManager(work_dir=folder)
    new_dbmgr._create_db()
    new_dbmgr.create_test_data()
    new_dbmgr.copy_uncopied_entries()

    # todo: fixes datenset dafür erzeugen, dass direkt geladen werden kann
    processor = SecXmlFileProcessor(new_dbmgr, folder)
    processor.downloadNumFiles()
    processor.downloadPreFiles()

    yield new_dbmgr
    shutil.rmtree(folder)

def test_parse_num_xml(dbmgr: DBManager):
    parser = SecXmlParser(dbmgr, data_dir=folder + "/data/")
    parser.parseNumFiles()

    print("end it")
