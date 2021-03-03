from _00_common.DBManagement import DBManager
import shutil


def test_create_db():
    shutil.rmtree("./data", ignore_errors=True)
    dbm = DBManager(work_dir="./data")
    dbm.find_missing_xbrl_ins_urls()
