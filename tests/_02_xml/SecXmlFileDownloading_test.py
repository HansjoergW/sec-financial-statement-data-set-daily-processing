import os
import shutil

import pytest
from secdaily._02_xml.db.XmlFileDownloadingDataAccess import XmlFileDownloadingDA
from secdaily._02_xml.SecXmlFileDownloading import SecXmlFileDownloader

scriptpath = os.path.realpath(__file__ + "/..")
folder = scriptpath + "/tmp"


@pytest.fixture(scope="module")
def dbmgr():
    shutil.rmtree(folder, ignore_errors=True)
    new_dbmgr = XmlFileDownloadingDA(work_dir=folder)
    new_dbmgr.create_db()
    new_dbmgr.create_test_data()
    yield new_dbmgr
    shutil.rmtree(folder)


def test_download_num_xml(dbmgr: XmlFileDownloadingDA):
    processor = SecXmlFileDownloader(dbmgr, folder)

    processor.downloadNumFiles()

    with_missing_nums = dbmgr.find_missing_xmlNumFiles()
    assert len(with_missing_nums) == 0


def test_download_pre_xml(dbmgr: XmlFileDownloadingDA):
    processor = SecXmlFileDownloader(dbmgr, folder)

    processor.downloadPreFiles()

    with_missing_pres = dbmgr.find_missing_xmlPreFiles()
    assert len(with_missing_pres) == 0
