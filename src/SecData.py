from _00_common.DBManagement import DBManager
from _01_index.SecIndexFileProcessing import SecIndexFileProcessor
from _01_index.SecIndexFilePostProcessing import SecIndexFilePostProcessor
from _02_xml.SecXmlFilePreProcessing import SecXmlFilePreprocessor
from _02_xml.SecXmlFileDownloading import SecXmlFileDownloader
from _02_xml.SecXmlFileParsing import SecXmlParser
from _03_dailyzip.DailyZipCreating import DailyZipCreator

import logging
from datetime import datetime, date
import dateutil


class SecDataOrchestrator:

    def __init__(self, workdir: str, year: int = None, month: int = None, months: int = 4):
        if workdir[-1] != '/':
            workdir = workdir + '/'

        self.workdir = workdir
        self.feeddir = workdir + "feed/"
        self.xmldir = workdir + "xml/"
        self.csvdir = workdir + "csv/"
        self.dailyzipdir = workdir + "daily/"

        self.dbmanager = DBManager(work_dir=workdir)

        self.today = datetime.today()
        if month is None:
            self.current_month = self.today.month
        else:
            self.current_month = month

        if year is None:
            self.current_year = self.today.year
        else:
            self.current_year = year

        current_date = date(self.current_year, self.current_month, 1)
        delta_month = dateutil.relativedelta.relativedelta(months=months)
        start_date = current_date - delta_month
        self.start_month = start_date.month
        self.start_year = start_date.year

        # logging.basicConfig(filename='logging.log',level=logging.DEBUG)
        logging.basicConfig(level=logging.INFO)

    def _log_main_header(self, title:str):
        logging.info("==============================================================")
        logging.info(title)
        logging.info("==============================================================")

    def _log_sub_header(self, title:str):
        logging.info("")
        logging.info("--------------------------------------------------------------")
        logging.info(title)
        logging.info("--------------------------------------------------------------")


    def _download_index_data(self):
        self._log_sub_header('download xbrl-rss index file data')
        secindexprocessor = SecIndexFileProcessor(self.dbmanager, self.start_year, self.current_year, self.start_month, self.current_month, self.feeddir)
        secindexprocessor.download_sec_feeds()

    def _postprocess_index_data(self):
        self._log_sub_header('add missing num-data file urls')
        secindexpostprocessor = SecIndexFilePostProcessor(self.dbmanager)
        secindexpostprocessor.add_missing_xbrlinsurl()
        self._log_sub_header('check for duplicates')
        secindexpostprocessor.check_for_duplicated()

    def process_index_data(self):
        self._log_main_header("Process xbrl-rss index files")
        self._download_index_data()
        self._postprocess_index_data()

    def _preprocess_xml(self):
        self._log_sub_header('preprocess xml files')
        secxmlfilepreprocessor = SecXmlFilePreprocessor(self.dbmanager)
        secxmlfilepreprocessor.copy_entries_to_processing_table()

    def _download_xml(self):
        secxmlfilesdownloader = SecXmlFileDownloader(self.dbmanager, self.xmldir)
        self._log_sub_header('download num xml files')
        secxmlfilesdownloader.downloadNumFiles()
        self._log_sub_header('download pre xml files')
        secxmlfilesdownloader.downloadPreFiles()

    def _parse_xml(self):
        secxmlfileparser = SecXmlParser(self.dbmanager, self.csvdir)
        self._log_sub_header('parse num xml files')
        secxmlfileparser.parseNumFiles()
        self._log_sub_header('parse pre xml files')
        secxmlfileparser.parsePreFiles()

    def process_xml_data(self):
        self._log_main_header("Process xbrl data files")

        self._preprocess_xml()
        self._download_xml()
        self._parse_xml()

    def create_daily_zip(self):
        self._log_main_header("Create daily zip files")
        zip_creator = DailyZipCreator(self.dbmanager, self.dailyzipdir)
        zip_creator.process()

    def process(self):
        self.process_index_data()
        self.process_xml_data()
        self.create_daily_zip()


if __name__ == '__main__':
    workdir_default = "d:/secprocessing/"
    # orchestrator = SecDataOrchestrator(workdir_default)
    orchestrator = SecDataOrchestrator(workdir_default, 2021, 6, 4)
    orchestrator.process()

