from _00_common.DBManagement import DBManager
from _02_xml.SecXmlFileProcessing import SecXmlFileProcessor
from _02_xml.SecXmlFileParsing import SecXmlParser
import shutil
import pytest
import glob

folder = "./tmp"

@pytest.fixture(scope="module")
def dbmgr():
    shutil.rmtree(folder, ignore_errors=True)
    new_dbmgr = DBManager(work_dir=folder)
    new_dbmgr._create_db()
    new_dbmgr.create_test_data()
    new_dbmgr.create_processing_test_data()

    yield new_dbmgr
    shutil.rmtree(folder)

def test_parse_num_xml(dbmgr: DBManager):
    parser = SecXmlParser(dbmgr, data_dir=folder + "/data/")
    parser.parseNumFiles()

    files = glob.glob("./tmp/data/*/*.csv")
    assert len(files) == 7

def test_parse_pre_xml(dbmgr: DBManager):
    parser = SecXmlParser(dbmgr, data_dir=folder + "/data/")
    parser.parsePreFiles()

    files = glob.glob("./tmp/data/*/*.csv")
    assert len(files) == 7
