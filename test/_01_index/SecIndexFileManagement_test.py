from _01_index.SecIndexFileParsing import SecIndexFileParser
import shutil
import os
import pytest

folder = "./tmp"


@pytest.fixture(scope="module")
def file():
    new_sec_file = SecIndexFileParser(2020, 12, folder)
    yield new_sec_file
    shutil.rmtree(folder)


def test_download(file: SecIndexFileParser):
    file.download_sec_feed()

    assert os.path.isfile(file.feed_file)


def test_parse(file: SecIndexFileParser):
    file.download_sec_feed()
    result = file.parse_sec_rss_feeds()
    assert len(result) > 0