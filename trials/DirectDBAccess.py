from _00_common.DBManagement import DBManager
import shutil
import pytest


def test_duplicates():
    workdir_default = "d:/secprocessing/"
    new_dbmgr = DBManager(workdir_default)

    duplicated = new_dbmgr.find_duplicated_adsh()
    print(duplicated)

    for dp in duplicated:
        new_dbmgr.mark_duplicated_adsh(dp)


