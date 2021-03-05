from _02_xml.SecFileManagement import SecIndexFile
import shutil
import os

folder = "./tmp"


def test_download():
    file = SecIndexFile(2020, 12, folder)
    file.download_sec_feed()
    assert os.path.isfile(file.feed_file)
    shutil.rmtree(folder)


def test_parse():
    file = SecIndexFile(2020, 12, folder)
    file.download_sec_feed()
    result = file.parse_sec_rss_feeds()

    assert len(result) > 0
    shutil.rmtree(folder)