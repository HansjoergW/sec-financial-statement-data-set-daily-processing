from _00_common.DBManagement import DBManager
from _00_common.SecFileUtils import get_url_content
from _01_index.SecIndexFileParsing import SecIndexFileParser

import logging
import datetime
from typing import Dict, List
import json
import re

from dataclasses import dataclass, field


@dataclass
class FiledReportEntry:
    cik: str
    name: str
    type: str
    filed: str
    filename: str
    reportjson: str = field(init=False)

    def __post_init__(self):
        self.reportjson = self.filename.replace("-","")[:-4] + "/index.json"
        self.filed = self.filed.replace("-","")


ten_report_matcher = re.compile(r".*[|]10-[KQ][|].*")
last_date_received_matcher = re.compile(r"Last Data Received:.*")
month_to_qrtr = {1: 1, 2: 1, 3: 1, 4: 2, 5: 2, 6: 2, 7: 3, 8: 3, 9: 3, 10: 4, 11: 4, 12: 4}


class SecFullIndexFileProcessor:
    """
    - downloads the desired sec files, parses them and adds the information into the db.
    - uses the fullindex to find new data
    """
    full_index_root_url = "https://www.sec.gov/Archives/edgar/full-index/"

    def __init__(self, dbmanager: DBManager, start_year: int, start_qrtr: int = 1, feed_dir: str = "./tmp/"):
        self.dbmanager = dbmanager
        self.start_year = start_year
        self.start_qrtr = start_qrtr
        self.feed_dir = feed_dir
        self.processdate = datetime.date.today().isoformat()

        self.current_year = datetime.datetime.now().year
        self.current_qrtr = month_to_qrtr[datetime.datetime.now().month]
        self.current_check = self.current_year * 10 + self.current_qrtr

    def _get_file_for_qrtr(self, year, qrtr):
        return get_url_content(f"{self.full_index_root_url}{year}/QTR{qrtr}/xbrl.idx")

    def get_next_index_file_iter(self):
        current_iter_year = self.start_year
        current_iter_qrtr = self.start_qrtr

        while True:
            yield current_iter_year, current_iter_qrtr, self._get_file_for_qrtr(current_iter_year, current_iter_qrtr)
            current_iter_qrtr += 1

            if current_iter_qrtr > 4:
                current_iter_qrtr = 1
                current_iter_year += 1

            if (current_iter_year * 10 + current_iter_qrtr) > self.current_check:
                break

    def parse_index_files(self):
        for year, qrtr, content in self.get_next_index_file_iter():
            last_date_received = last_date_received_matcher.search(content).group(0)
            last_date_received = last_date_received.split(":")[1].strip()
            ten_report_entries = ten_report_matcher.findall(content)

            ten_report_entries_splitted = [x.split('|') for x in ten_report_entries]
            ten_report_entries = [FiledReportEntry(x[0], x[1], x[2], x[3], x[4]) for x in ten_report_entries_splitted]

            yield year, qrtr, last_date_received, ten_report_entries

            nächstes: prüfen, ob eine datei nicht bereits komplett verarbeitet worden ist.
            -> vermutlich neue tabelle, die das trackt.







if __name__ == '__main__':
    new_dbmgr = DBManager(work_dir="./tmp")
    # new_dbmgr._create_db()
    processor = SecFullIndexFileProcessor(new_dbmgr, 2019, 2)
    processor.parse_index_files()
