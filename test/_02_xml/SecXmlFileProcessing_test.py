from _00_common.DBManagement import DBManager
from _02_xml.SecXmlFileDownloading import SecXmlFileDownloader
import shutil
import pytest
import os

scriptpath = os.path.realpath(__file__ + "/..")
folder = scriptpath + "/tmp"

@pytest.fixture(scope="module")
def dbmgr():
    shutil.rmtree(folder, ignore_errors=True)
    new_dbmgr = DBManager(work_dir=folder)
    new_dbmgr._create_db()
    new_dbmgr.create_test_data()
    new_dbmgr.copy_uncopied_entries()
    yield new_dbmgr
    shutil.rmtree(folder)

def test_download_num_xml(dbmgr: DBManager):
    processor = SecXmlFileDownloader(dbmgr, folder)

    processor.downloadNumFiles()

    df_pro = dbmgr.read_all_processing()
    assert sum(df_pro.xmlNumFile.isnull()) == 0


def test_download_pre_xml(dbmgr: DBManager):
    processor = SecXmlFileDownloader(dbmgr, folder)

    processor.downloadPreFiles()

    df_pro = dbmgr.read_all_processing()
    assert sum(df_pro.xmlPreFile.isnull()) == 0