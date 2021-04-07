from _00_common.DBManagement import DBManager
import shutil
import pytest

folder = "./data"


@pytest.fixture(scope="module")
def dbm():
    shutil.rmtree("./data", ignore_errors=True)
    new_dbmgr = DBManager(work_dir=folder)
    new_dbmgr._create_db()
    new_dbmgr.create_test_data()
    yield new_dbmgr
    shutil.rmtree(folder)

def test_create_db(dbm: DBManager):
    dbm.find_missing_xbrl_ins_urls()

def test_get_adsh_by_feed_file(dbm: DBManager):
    result = dbm.get_adsh_by_feed_file('file1.xml')

    assert len(result) == 7