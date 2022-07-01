from _01_index.SecFullIndexFileProcessing import SecFullIndexFileProcessor
from _01_index.SecFullIndexFilePostProcessing import SecFullIndexFilePostProcessor
from _01_index.db.IndexPostProcessingDataAccess import IndexPostProcessingDA
from _01_index.db.IndexProcessingDataAccess import IndexProcessingDA
from _02_xml.SecXmlFilePreProcessing import SecXmlFilePreprocessor
from _02_xml.SecXmlFileDownloading import SecXmlFileDownloader
from _02_xml.SecXmlFileParsing import SecXmlParser
from _02_xml.db.XmlFilePreProcessingDataAccess import XmlFilePreProcessingDA
from _02_xml.db.XmlFileDownloadingDataAccess import XmlFileDownloadingDA
from _02_xml.db.XmlFileParsingDataAccess import XmlFileParsingDA
from _03_dailyzip.DailyZipCreating import DailyZipCreator
from _04_seczip.SecZipDownloading import SecZipDownloader
from _03_dailyzip.db.DailyZipCreatingDataAccess import DailyZipCreatingDA

import logging
from datetime import datetime, date
import dateutil


month_to_qrtr = {1: 1, 2: 1, 3: 1, 4: 2, 5: 2, 6: 2, 7: 3, 8: 3, 9: 3, 10: 4, 11: 4, 12: 4}


class SecDataOrchestrator:

    def __init__(self, workdir: str, start_year: int = None, start_qrtr: int = None):
        """
        """
        if workdir[-1] != '/':
            workdir = workdir + '/'

        self.workdir = workdir
        self.feeddir = workdir + "feed/"
        self.xmldir = workdir + "xml/"
        self.csvdir = workdir + "csv/"
        self.dailyzipdir = workdir + "daily/"
        self.seczipdir = workdir + "quarterzip/"

        self.today = datetime.today()

        if start_year is None:
            self.start_year = self.today.year
            self.start_qrtr = month_to_qrtr[self.today.month]
            if start_qrtr is not None:
                logging.info("set 'start_qrtr' is ignored, since 'start_year' is not set")
        else:
            self.start_year = start_year
            if start_qrtr is None:
                self.start_qrtr = 1
            else:
                self.start_qrtr = start_qrtr

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
        self._log_sub_header('looking for new reports')
        secfullindexprocessor = SecFullIndexFileProcessor(IndexProcessingDA(self.workdir), self.start_year, self.start_qrtr)
        secfullindexprocessor.process()

    def _postprocess_index_data(self):
        self._log_sub_header('add xbrl file urls')
        secfullindexpostprocessor = SecFullIndexFilePostProcessor(IndexPostProcessingDA(self.workdir))
        secfullindexpostprocessor.process()
        self._log_sub_header('check for duplicates')
        secfullindexpostprocessor.check_for_duplicated()

    def process_index_data(self):
        self._log_main_header("Process xbrl full index files")
        self._download_index_data()
        self._postprocess_index_data()

    def _preprocess_xml(self):
        self._log_sub_header('preprocess xml files')
        secxmlfilepreprocessor = SecXmlFilePreprocessor(XmlFilePreProcessingDA(self.workdir))
        secxmlfilepreprocessor.copy_entries_to_processing_table()

    def _download_xml(self):
        secxmlfilesdownloader = SecXmlFileDownloader(XmlFileDownloadingDA(self.workdir), self.xmldir)
        self._log_sub_header('download num xml files')
        secxmlfilesdownloader.downloadNumFiles()
        self._log_sub_header('download pre xml files')
        secxmlfilesdownloader.downloadPreFiles()

    def _parse_xml(self):
        secxmlfileparser = SecXmlParser(XmlFileParsingDA(self.workdir), self.csvdir)
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
        zip_creator = DailyZipCreator(DailyZipCreatingDA(self.workdir), self.dailyzipdir)
        zip_creator.process()

    def download_seczip(self):
        self._log_main_header("Download Seczip files")
        downloader = SecZipDownloader(self.seczipdir)
        downloader.download()

    def process(self):
        self.process_index_data()
        self.process_xml_data()
        self.create_daily_zip()
        self.download_seczip()


if __name__ == '__main__':
    workdir_default = "d:/secprocessing/"
    # orchestrator = SecDataOrchestrator(workdir_default)
    orchestrator = SecDataOrchestrator(workdir_default, 2022, 2)
    orchestrator.process()

