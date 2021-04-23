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


def test_sec_index_file(dbm: DBManager):
    dbm.insert_index_file("first.xml","2021-01-01")
    df = dbm.read_all_index_files()

    assert len(df) == 1
    assert df[df.sec_feed_file == 'first.xml'].status.values[0] == "progress"
    assert df[df.sec_feed_file == 'first.xml'].processdate.values[0] == "2021-01-01"

    dbm.insert_index_file("second.xml","2021-01-01")
    df = dbm.read_all_index_files()

    assert len(df) == 2
    assert df[df.sec_feed_file == 'first.xml'].status.values[0] == "done"
    assert df[df.sec_feed_file == 'second.xml'].status.values[0] == "progress"

    dbm.update_index_file('second.xml','2021-01-02')
    df = dbm.read_all_index_files()

    assert len(df) == 2
    assert df[df.sec_feed_file == 'first.xml'].status.values[0] == "done"
    assert df[df.sec_feed_file == 'second.xml'].processdate.values[0] == "2021-01-02"


def test_copy_uncopied_entries(dbm: DBManager):
    copied_entries = dbm.copy_uncopied_entries()

    df_feeds = dbm.read_all()
    df_processing = dbm.read_all_processing()

    assert sum(df_feeds.status.isnull()) == 0
    assert len(df_processing) == copied_entries

