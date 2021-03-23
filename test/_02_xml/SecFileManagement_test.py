from _02_xml.SecIndexFileManagement import SecIndexFile
import shutil
import os
import pytest

folder = "./tmp"


@pytest.fixture(scope="module")
def file():
    new_sec_file = SecIndexFile(2020, 12, folder)
    yield new_sec_file
    shutil.rmtree(folder)


def test_download(file: SecIndexFile):
    file.download_sec_feed()

    assert os.path.isfile(file.feed_file)


def test_parse(file: SecIndexFile):
    file.download_sec_feed()
    result = file.parse_sec_rss_feeds()
    assert len(result) > 0