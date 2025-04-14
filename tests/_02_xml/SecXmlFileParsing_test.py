import glob
import os
from pathlib import Path

import pytest
from secdaily._02_xml.db.XmlFileParsingDataAccess import XmlFileParsingDA
from secdaily._02_xml.SecXmlFileParsing import SecXmlParser

scriptpath = os.path.realpath(__file__ + "/..")


@pytest.fixture
def dbmgr(tmp_path):
    new_dbmgr = XmlFileParsingDA(work_dir=str(tmp_path))
    new_dbmgr.create_db()
    new_dbmgr.create_test_data()
    new_dbmgr.create_processing_test_data()

    yield new_dbmgr


def test_parse_num_xml(dbmgr: XmlFileParsingDA, tmp_path: Path):
    parser = SecXmlParser(dbmanager=dbmgr, data_dir=str(tmp_path) + "/data/")
    parser.parseNumFiles()

    files = glob.glob(str(tmp_path) + "/data/*/*/*num.csv.zip")
    assert len(files) == 7

    unparsed_num_files = dbmgr.find_unparsed_numFiles()
    assert 0 == len(unparsed_num_files)


def test_parse_pre_xml(dbmgr: XmlFileParsingDA, tmp_path: Path):
    parser = SecXmlParser(dbmgr, data_dir=str(tmp_path) + "/data/")
    parser.parsePreFiles()

    files = glob.glob(str(tmp_path) + "/data/*/*/*pre.csv.zip")
    assert 7 == len(files)

    unparsed_pre_files = dbmgr.find_unparsed_preFiles()
    assert 0 == len(unparsed_pre_files)
