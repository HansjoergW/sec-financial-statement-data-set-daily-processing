from _00_common.DBManagement import DBManager
from _01_index.SecIndexFilePostProcessing import SecIndexFilePostProcessor
import shutil
import pytest
import os

scriptpath = os.path.realpath(__file__ + "/..")
folder = scriptpath + "/tmp"

@pytest.fixture(scope="module")
def dbmgr():
    new_dbmgr = DBManager(work_dir=folder)
    new_dbmgr._create_db()
    new_dbmgr.create_test_data()
    yield new_dbmgr
    shutil.rmtree(folder)


def test_add_missing_xbrlinsurl(dbmgr: DBManager):
    sut = SecIndexFilePostProcessor(dbmgr)
    sut.add_missing_xbrlinsurl()