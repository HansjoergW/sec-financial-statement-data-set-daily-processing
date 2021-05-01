from _00_common.DBManagement import DBManager
from _01_index.SecIndexFileProcessing import SecIndexFileProcessor
from _01_index.SecIndexFilePostProcessing import SecIndexFilePostProcessor
from _02_xml.SecXmlFileProcessing import SecXmlFileProcessor
from _02_xml.SecXmlFileParsing import SecXmlParser

import logging
from datetime import datetime
import dateutil


class SecXMLProcessingOrchestrator():

    def __init__(self, workdir: str):
        if workdir[-1] != '/':
            workdir = workdir + '/'

        self.workdir = workdir
        self.feeddir = workdir + "feed/"
        self.xmldir = workdir + "xml/"
        self.csvdir = workdir + "csv/"

        self.dbmanager = DBManager(work_dir=workdir)

        self.today = datetime.today()
        self.current_month = self.today.month
        self.current_year = self.today.year

        delta_month = dateutil.relativedelta.relativedelta(months=4)
        start_date = self.today - delta_month
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
        secxmlfilesprocessor = SecXmlFileProcessor(self.dbmanager, self.xmldir)
        secxmlfilesprocessor.downloadNumFiles()
        secxmlfilesprocessor.downloadPreFiles()

    def _parse_xml(self):
        secxmlfileparser = SecXmlParser(self.dbmanager, self.csvdir)
        secxmlfileparser.parseNumFiles()
        secxmlfileparser.parsePreFiles()

    def process_xml_data(self):
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
    orchestrator = SecXMLProcessingOrchestrator(workdir_default)
    #orchestrator.process()
    orchestrator._parse_xml()
