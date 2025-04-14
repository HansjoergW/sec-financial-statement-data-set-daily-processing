import glob
import os
import shutil

import pytest
from secdaily._02_xml.db.XmlFileParsingDataAccess import XmlFileParsingDA
from secdaily._02_xml.SecXmlFileParsing import SecXmlParser

scriptpath = os.path.realpath(__file__ + "/..")
folder = scriptpath + "/tmp"


@pytest.fixture(scope="module")
def dbmgr():
    shutil.rmtree(folder, ignore_errors=True)
    new_dbmgr = XmlFileParsingDA(work_dir=folder)
    new_dbmgr.create_db()
    new_dbmgr.create_test_data()
    new_dbmgr.create_processing_test_data()

    yield new_dbmgr
    shutil.rmtree(folder)


def test_parse_num_xml(dbmgr: XmlFileParsingDA):
    parser = SecXmlParser(dbmanager=dbmgr, data_dir=folder + "/data/")
    parser.parseNumFiles()

    files = glob.glob(folder + "/data/*/*/*num.csv.zip")
    assert len(files) == 7

    unparsed_num_files = dbmgr.find_unparsed_numFiles()
    assert 0 == len(unparsed_num_files)


def test_parse_pre_xml(dbmgr: XmlFileParsingDA):
    parser = SecXmlParser(dbmgr, data_dir=folder + "/data/")
    parser.parsePreFiles()

    files = glob.glob(folder + "/data/*/*/*pre.csv.zip")
    assert 7 == len(files)

    unparsed_pre_files = dbmgr.find_unparsed_preFiles()
    assert 0 == len(unparsed_pre_files)
