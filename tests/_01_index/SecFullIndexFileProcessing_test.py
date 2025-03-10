from secdaily._01_index.db.IndexProcessingDataAccess import IndexProcessingDA
from secdaily._01_index.SecFullIndexFileProcessing import SecFullIndexFileProcessor
import shutil
import pytest
import os


scriptpath = os.path.realpath(__file__ + "/..")
folder = scriptpath + "/tmp"


@pytest.fixture(scope="module")
def dbmgr():
    new_dbmgr = IndexProcessingDA(work_dir=folder)
    new_dbmgr._create_db()
    yield new_dbmgr
    shutil.rmtree(folder)


def test_init(dbmgr: IndexProcessingDA):
    processor = SecFullIndexFileProcessor(dbmanager=dbmgr,
                                          start_year=2022,
                                          start_qrtr=1,
                                          feed_dir=folder,
                                          urldownloader=None)
