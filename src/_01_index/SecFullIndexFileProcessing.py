from _00_common.DBManagement import DBManager
from _00_common.SecFileUtils import get_url_content
from _01_index.SecIndexFileParsing import SecIndexFileParser

import logging
import datetime
from typing import Dict, List, Tuple, Optional
import json
import re
import shutil

import pandas as pd

from dataclasses import dataclass, field, asdict
from multiprocessing import Pool

from time import time, sleep

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


@dataclass
class XbrlFile:
    url: str
    lastChange: str
    size: int


@dataclass
class XbrlFiles:
    accessionNumber: str
    xbrlIns: Optional[XbrlFile]
    xbrlPre: Optional[XbrlFile]
    xbrlCal: Optional[XbrlFile]
    xbrlDef: Optional[XbrlFile]
    xbrlLab: Optional[XbrlFile]


ten_report_matcher = re.compile(r".*[|]10-[KQ][|].*")
last_date_received_matcher = re.compile(r"Last Data Received:.*")
month_to_qrtr = {1: 1, 2: 1, 3: 1, 4: 2, 5: 2, 6: 2, 7: 3, 8: 3, 9: 3, 10: 4, 11: 4, 12: 4}


class SecFullIndexFileProcessor:
    """
    - downloads the desired sec files, parses them and adds the information into the db.
    - uses the fullindex to find new data
    """
    edgar_archive_root_url = "https://www.sec.gov/Archives/"
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
            # set sec_feed_file
            new_entries_save_df['sec_feed_file'] = pseudo_sec_feed_file

            new_entries_save_df.drop_duplicates('accessionNumber', inplace=True)
            new_entries_save_df.set_index('accessionNumber', inplace=True)

            logging.info("   read entries: {}".format(len(new_entries_save_df)))

            # updaten -> status table
            self.dbmanager.insert_feed_info(new_entries_save_df)
            self.dbmanager.update_status_fullindex_file(year, qrtr, last_date_received)


    @staticmethod
    def _find_xbrl_files(data: Tuple[str, str, str, str]) -> XbrlFiles:
        adsh = data[0]
        report_json = data[3]

        index_json_url = SecFullIndexFileProcessor.edgar_archive_root_url + report_json

        # pre ist immer mit "_pre.xml"
        # num ist entweder mit selben namen wie "_pre.xml" einfach mit ".xml" oder dann Endung mit "_htm.xml" manchmal auch noch mit 10q oder 10k im Text
        #
        # Variante wäre es, das xbrl zip runterzuladen und zu speichern, da ist auch die taxonomy und struktur definiert
        # -> im xsd Evtl. könnte das beim folgenden parsen nützlich sein

        try:
            content = get_url_content(index_json_url)
            json_content = json.loads(content)
            struktur ist "directory/item/->Liste mit [last-modified, name, type, size]" wobei size auch leer sein kann
            suchen nach -xbrl.zip, *.xml
            print("*")
            return None
        except:
            return XbrlFiles(adsh, None, None, None, None, None)

    @staticmethod
    def _find_main_file_throttle(data_tuple: Tuple[str, str, str, str]) -> Tuple[str, str, str]:
        # ensures that only one request per second is send
        start = time()
        new_url, size, accession_nr = SecFullIndexFileProcessor._find_xbrl_files(data_tuple)
        end = time()
        sleep((1000-(end - start)) / 1000)
        return new_url, size, accession_nr

    def complete_xbrl_file_information(self):
        # das nächste problem ist es die Namen der Dateien zu finden, das geht nur über
        # einen zusätzlices laden der json index datei pro report..
        # das müsste dann wieder parallel gemacht werden.
        pool = Pool(8)

        last_missing: int = None
        missing: List[Tuple[str, str, str, str]] = self.dbmanager.find_entries_with_missing_xbrl_ins_or_pre()
        while (last_missing is None) or (last_missing > len(missing)):
            last_missing = len(missing)
            logging.info("missing entries " + str(len(missing)))

            for i in range(0, len(missing), 100):
                chunk = missing[i:i + 100]
                update_data: List[Tuple[str, str, str]] = pool.map(SecFullIndexFileProcessor._find_main_file_throttle, chunk)
                self.dbmanager.update_xbrl_ins_urls(update_data)
                logging.info("commited chunk: " + str(i))

            missing = self.dbmanager.find_entries_with_missing_xbrl_ins_or_pre()

        if len(missing) > 0:
            logging.info("Failed to add missing for " + str(len(missing)))

    def process(self):
        self.find_new_reports()
        self.complete_xbrl_file_information()



if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.DEBUG)
    test_reports = [
        "edgar/data/1000045/000095017022000940/index.json",
        "edgar/data/1000209/000095017022003603/index.json",
        "edgar/data/1000228/000100022822000016/index.json",
        "edgar/data/1000229/000095017022001087/index.json",
        "edgar/data/1000230/000143774922006521/index.json",
        "edgar/data/1000298/000155837022003437/index.json",
        "edgar/data/1000623/000100062322000016/index.json",
        "edgar/data/1000683/000121390022016788/index.json"
        ]

    adsh = None
    report_index_json_url = test_reports[0]
    SecFullIndexFileProcessor._find_xbrl_files((adsh, None, None, report_index_json_url))

    # folder = "./tmp"
    # try:
    #     new_dbmgr = DBManager(work_dir=folder)
    #     new_dbmgr._create_db()
    #     processor = SecFullIndexFileProcessor(new_dbmgr, 2022, 1)
    #     processor.process()
    # finally:
    #     shutil.rmtree(folder)
