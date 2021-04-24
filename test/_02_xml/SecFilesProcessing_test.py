from _00_common.DBManagement import DBManager
from _02_xml.SecFilesProcessing import SecIndexFilesProcessor, SecXmlFilesProcessor
import shutil
import pytest
import logging

folder = "./tmp"

@pytest.fixture(scope="module")
def dbmgr():
    new_dbmgr = DBManager(work_dir=folder)
    new_dbmgr._create_db()
    yield new_dbmgr
    shutil.rmtree(folder)


def test_multidownload(dbmgr: DBManager):
    processor = SecIndexFilesProcessor(dbmgr, 2021, 2021, 1, 2, feed_dir=folder)
    processor.download_sec_feeds()
    data = dbmgr.read_all()
    assert len(data) > 0


def test_download_num_xml(dbmgr: DBManager):
    processor = SecXmlFilesProcessor(dbmgr, folder)
    dbmgr.create_test_data()
    dbmgr.copy_uncopied_entries()

    processor.downloadNumFiles()

    df_pro = dbmgr.read_all_processing()
    assert sum(df_pro.xmlNumFile.isnull()) == 0


def test_download_pre_xml(dbmgr: DBManager):
    processor = SecXmlFilesProcessor(dbmgr, folder)
    dbmgr.create_test_data()
    dbmgr.copy_uncopied_entries()

    processor.downloadPreFiles()

    df_pro = dbmgr.read_all_processing()
    assert sum(df_pro.xmlPreFile.isnull()) == 0