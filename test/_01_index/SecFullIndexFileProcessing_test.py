from _00_common.DBManagement import DBManager
from _01_index.SecFullIndexFileProcessing import SecFullIndexFileProcessor
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


def test_init(dbmgr: DBManager):
    processor = SecFullIndexFileProcessor(dbmgr, 2022, 2022, 1, 2, feed_dir=folder)
