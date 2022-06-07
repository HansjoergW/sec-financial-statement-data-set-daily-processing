from _00_common.DBManagement import DBManager
from _00_common.SecFileUtils import get_url_content

import logging
import datetime
from typing import Dict, List, Tuple, Optional
import re
import shutil

import pandas as pd

from dataclasses import dataclass, field, asdict


@dataclass
class FiledReportEntry:
    cikNumber: str
    companyName: str
    formType: str
    filingDate: str
    filename: str
    accessionNumber: str = field(init=False)
    reportJson: str = field(init=False)

    def __post_init__(self):
        filename_no_ext = self.filename[:-4]
        cleaned_filename = filename_no_ext.replace("-","")
        self.reportJson = cleaned_filename + "/index.json"
        self.accessionNumber = filename_no_ext[filename_no_ext.rfind("/") + 1:]


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

        self.full_index_status_df = dbmanager.read_all_fullindex_files()

    def _get_file_for_qrtr(self, year, qrtr):
        return get_url_content(f"{self.full_index_root_url}{year}/QTR{qrtr}/xbrl.idx")

    def get_next_index_file_iter(self):
        """
        Creates an iterator that iterates over all quarterly full index file starting with the configured
        start_year and start_qrtr
        it returns the year, quarter, content of the full index file of that quarter
        """

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

    def parsed_index_file_iter(self):
        for year, qrtr, content in self.get_next_index_file_iter():
            last_date_received = last_date_received_matcher.search(content).group(0)
            last_date_received = last_date_received.split(":")[1].strip()
            ten_report_entries = ten_report_matcher.findall(content)

            # check whether the entry already was processed and didn't have any updates
            # so only entries are returned that either are new or which content has changed
            entry_df = self.full_index_status_df[(self.full_index_status_df.year == year) & (self.full_index_status_df.quarter == qrtr)]
            if not entry_df.empty:
                if entry_df.iloc[0].state == last_date_received:
                    logging.info("- already processed {}/{} -> skip ".format(qrtr, year))
                    continue
                else:
                    logging.info("- updates for {}/{} ".format(qrtr, year))
                    self.dbmanager.update_fullindex_file(year, qrtr, self.processdate)
            else:
                logging.info("- new file for {}/{} ".format(qrtr, year))
                self.dbmanager.insert_fullindex_file(year, qrtr, self.processdate)

            ten_report_entries_splitted = [x.split('|') for x in ten_report_entries]
            ten_report_entries = [asdict(FiledReportEntry(x[0], x[1], x[2], x[3], x[4])) for x in ten_report_entries_splitted]
            ten_report_entries_df = pd.DataFrame(ten_report_entries)
            yield year, qrtr, last_date_received, ten_report_entries_df

    def find_new_reports(self):


        for year, qrtr, last_date_received, ten_report_entries_df in self.parsed_index_file_iter():
            pseudo_sec_feed_file =  f"fullindex-{year}-QTR{qrtr}.json"

            # read the entries that already were processed
            existing_adshs = self.dbmanager.get_adsh_by_feed_file(pseudo_sec_feed_file)
            new_entries_df = ten_report_entries_df[~ten_report_entries_df.accessionNumber.isin(existing_adshs)]

            new_entries_save_df = new_entries_df[['accessionNumber', 'companyName', 'formType','filingDate','cikNumber', 'reportJson']].copy()

            # filingDate -> as Date
            new_entries_save_df['filingDate'] = pd.to_datetime(new_entries_save_df.filingDate, format="%Y-%m-%d")
            # calculate filingMonth, filingYear
            new_entries_save_df['filingMonth'] = new_entries_save_df.filingDate.dt.month
            new_entries_save_df['filingYear'] = new_entries_save_df.filingDate.dt.year

            new_entries_save_df['filingDate'] = new_entries_save_df.filingDate.dt.strftime("%m/%d/%Y")
            new_entries_save_df['cikNumber'] = new_entries_save_df.cikNumber.astype(str)
            new_entries_save_df['cikNumber'] = new_entries_save_df.cikNumber.str.zfill(10)

            # set sec_feed_file
            new_entries_save_df['sec_feed_file'] = pseudo_sec_feed_file

            new_entries_save_df.drop_duplicates('accessionNumber', inplace=True)
            new_entries_save_df.set_index('accessionNumber', inplace=True)

            logging.info("   read entries: {}".format(len(new_entries_save_df)))

            # updaten -> status table
            self.dbmanager.insert_feed_info(new_entries_save_df)
            self.dbmanager.update_status_fullindex_file(year, qrtr, last_date_received)

    def process(self):
        self.find_new_reports()


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.DEBUG)
    folder = "./tmp"
    try:
        new_dbmgr = DBManager(work_dir=folder)
        new_dbmgr._create_db()
        processor = SecFullIndexFileProcessor(new_dbmgr, 2022, 1)
        processor.process()
    finally:
        shutil.rmtree(folder)
