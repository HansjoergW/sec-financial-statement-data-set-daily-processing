from _00_common.DBManagement import DBManager
from _01_index.SecIndexFileProcessing import SecIndexFileProcessor
from _01_index.SecIndexFilePostProcessing import SecIndexFilePostProcessor
from _02_xml.SecXmlFileDownloading import SecXmlFileDownloader
from _02_xml.SecXmlFileParsing import SecXmlParser

import logging
from datetime import datetime, date
import dateutil


class SecDataOrchestrator():

    def __init__(self, workdir: str, current_year: int = None, current_month: int = None, months: int = 4):
        if workdir[-1] != '/':
            workdir = workdir + '/'

        self.workdir = workdir
        self.feeddir = workdir + "feed/"
        self.xmldir = workdir + "xml/"
        self.csvdir = workdir + "csv/"

        self.dbmanager = DBManager(work_dir=workdir)

        self.today = datetime.today()
        if current_month is None:
            self.current_month = self.today.month
        else:
            self.current_month = current_month

        if current_year is None:
            self.current_year = self.today.year
        else:
            self.current_year = current_year

        current_date = date(self.current_year, self.current_month, 1)
        delta_month = dateutil.relativedelta.relativedelta(months=months)
        start_date = current_date - delta_month
        self.start_month = start_date.month
        self.start_year = start_date.year

        # logging.basicConfig(filename='logging.log',level=logging.DEBUG)
        logging.basicConfig(level=logging.INFO)

    def _download_index_data(self):
        secindexprocessor = SecIndexFileProcessor(self.dbmanager, self.start_year, self.current_year, self.start_month, self.current_month, self.feeddir)
        secindexprocessor.download_sec_feeds()

    def _postprocess_index_data(self):
        secindexpostprocessor = SecIndexFilePostProcessor(self.dbmanager)
        secindexpostprocessor.add_missing_xbrlinsurl()
        secindexpostprocessor.check_for_duplicated()

    def process_index_data(self):
        self._download_index_data()
        self._postprocess_index_data()

    def _download_xml(self):
        secxmlfilesdownloader = SecXmlFileDownloader(self.dbmanager, self.xmldir)
        secxmlfilesdownloader.downloadNumFiles()
        secxmlfilesdownloader.downloadPreFiles()

    def _parse_xml(self):
        secxmlfileparser = SecXmlParser(self.dbmanager, self.csvdir)
        secxmlfileparser.parseNumFiles()
        secxmlfileparser.parsePreFiles()

    def process_xml_data(self):
        # todo: sollte in eigene xml preprocessor klasse
        # move new entries in sec_feeds to sec_processing
        entries = self.dbmanager.copy_uncopied_entries()
        logging.info("{} entries copied into processing table".format(entries))

        self._download_xml()
        self._parse_xml()

    def process(self):
        self.process_index_data()
        self.process_xml_data()


if __name__ == '__main__':
    workdir_default = "d:/secprocessing/"
    # orchestrator = SecDataOrchestrator(workdir_default)
    orchestrator = SecDataOrchestrator(workdir_default, 2021, 5, 1)

    orchestrator.process()

