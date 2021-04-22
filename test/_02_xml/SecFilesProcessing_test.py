from _00_common.DBManagement import DBManager
from _02_xml.SecFilesProcessing import SecFilesProcessor
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
    processor = SecFilesProcessor(dbmgr, 2021, 2021, 1, 2, feed_dir=folder)
    processor.download_sec_feeds()
    data = dbmgr.read_all()
    assert len(data) > 0
