from _00_common.DBManagement import DBManager
from _00_common.SecFileUtils import get_url_content
from _01_index.SecIndexFileParsing import SecIndexFileParser

import logging
import datetime
from typing import Dict
import json


class SecFullIndexFileProcessor:

    """
    - downloads the desired sec files, parses them and adds the information into the db.
    - uses the fullindex to find new data
    """
    full_index_root_url = "https://www.sec.gov/Archives/edgar/full-index/"

    def __init__(self, dbmanager: DBManager, start_year:int, end_year: int, start_qrtr: int = 1, end_qrtr:int = 4, feed_dir: str = "./tmp/"):
        self.dbmanager = dbmanager
        self.start_year = start_year
        self.end_year = end_year
        self.start_qrtr = start_qrtr
        self.end_qrtr = end_qrtr
        self.feed_dir = feed_dir
        self.processdate = datetime.date.today().isoformat()


if __name__ == '__main__':
    new_dbmgr = DBManager(work_dir="./tmp")
    new_dbmgr._create_db()
    processor = SecFullIndexFileProcessor(new_dbmgr, 2022, 2022)