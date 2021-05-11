from src._00_common import DBManager
from src._01_index import SecIndexFileProcessor
import shutil
import pytest

folder = "./tmp"

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


