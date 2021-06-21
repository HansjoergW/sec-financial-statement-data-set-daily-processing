from _00_common.DBManagement import DBManager
from _01_index.SecIndexFileProcessing import SecIndexFileProcessor
import shutil
import pytest
import os

scriptpath = os.path.realpath(__file__ + "/..")
folder = scriptpath + "/tmp"


@pytest.fixture(scope="module")
def dbmgr():
    new_dbmgr = DBManager(work_dir=folder)
    new_dbmgr._create_db()
    yield new_dbmgr
    shutil.rmtree(folder)


def test_multidownload(dbmgr: DBManager):
    processor = SecIndexFileProcessor(dbmgr, 2021, 2021, 1, 2, feed_dir=folder)
    processor.download_sec_feeds()
    data = dbmgr.read_all()
    assert len(data) > 0
    index_data = dbmgr.read_all_index_files()
    assert len(index_data) == 2

    processor = SecIndexFileProcessor(dbmgr, 2021, 2021, 1, 3, feed_dir=folder)
    processor.download_sec_feeds()
    index_data = dbmgr.read_all_index_files()
    assert len(index_data) == 3


