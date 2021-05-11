from _00_common.DBManagement import DBManager
from _02_xml.SecXmlFileParsing import SecXmlParser
import shutil
import pytest
import glob
import os

scriptpath = os.path.realpath(__file__ + "/..")
folder = scriptpath + "/tmp"

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

    files = glob.glob(folder + "/data/*/*num.csv")
    assert len(files) == 7

    df = dbmgr.read_all_processing()
    assert 0 == sum(df.csvNumFile.isnull() | df.numParseState.isnull() | df.numParseDate.isnull())


def test_parse_pre_xml(dbmgr: DBManager):
    parser = SecXmlParser(dbmgr, data_dir=folder + "/data/")
    parser.parsePreFiles()

    files = glob.glob(folder + "/data/*/*num.csv")
    assert 7 == len(files)

    df = dbmgr.read_all_processing()
    assert 0 == sum(df.csvPreFile.isnull() | df.preParseState.isnull() | df.preParseDate.isnull())

