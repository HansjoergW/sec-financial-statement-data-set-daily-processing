from _00_common.DBManagement import DBManager
from _02_xml.SecFilesProcessing import SecFilesProcessor
from _02_xml.SecFeedDataManagement import SecFeedDataManager

import logging
from datetime import datetime
from typing import List
import dateutil


class SecProcessingOrchestrator():

    def __init__(self, workdir: str):
        self.workdir = workdir
        self.feeddir = workdir + "feed/"
        self.dbmanager = DBManager(work_dir=workdir)
        self.secfeeddatamgr = SecFeedDataManager(self.dbmanager)

        self.today = datetime.today()
        self.current_month = self.today.month
        self.current_year = self.today.year

        delta_month = dateutil.relativedelta.relativedelta(months=4)
        start_date = self.today - delta_month
        self.start_month = start_date.month
        self.start_year = start_date.year

        # logging.basicConfig(filename='logging.log',level=logging.DEBUG)
        logging.basicConfig(level=logging.INFO)

    def _process_sec_feed_data(self):
        secfilesprocessor = SecFilesProcessor(self.dbmanager, self.start_year, self.current_year, self.start_month, self.current_month, self.feeddir)
        secfilesprocessor.download_sec_feeds()

    def _complete_sec_feed_data(self):
        self.secfeeddatamgr.add_missing_xbrlinsurl()

    def _check_for_duplicated(self):
        duplicated_adshs: List[str] = self.dbmanager.find_duplicated_adsh()
        for duplicated in duplicated_adshs:
            logging.info("Found duplicated: " + duplicated)
            self.dbmanager.mark_duplicated_adsh(duplicated)

    def get_filing_information(self):
        self._process_sec_feed_data()
        self._complete_sec_feed_data()
        self._check_for_duplicated()
        # -> Schritt bereinigen von doppelten einträgen

if __name__ == '__main__':
    workdir_default = "d:/secprocessing/"
    orchestrator = SecProcessingOrchestrator(workdir_default)
    #orchestrator.get_filing_information()
    orchestrator._complete_sec_feed_data()
