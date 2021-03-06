from _00_common.DBManagement import DBManager
from _02_xml.SecFeedDataManagement import SecFeedDataManager
import shutil
import os
import pytest

folder = "./tmp"


@pytest.fixture(scope="module")
def dbmgr():
    new_dbmgr = DBManager(work_dir=folder)
    new_dbmgr.create_test_data()
    yield new_dbmgr
    shutil.rmtree(folder)


def test_add_missing_xbrlinsurl(dbmgr: DBManager):
    sut = SecFeedDataManager(dbmgr)
    sut.add_missing_xbrlinsurl()