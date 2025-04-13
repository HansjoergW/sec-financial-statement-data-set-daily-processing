import logging
from datetime import datetime
from typing import Optional

from secdaily._00_common.BaseDefinitions import MONTH_TO_QRTR
from secdaily._00_common.DownloadUtils import UrlDownloader
from secdaily._01_index.db.IndexPostProcessingDataAccess import IndexPostProcessingDA
from secdaily._01_index.db.IndexProcessingDataAccess import IndexProcessingDA
from secdaily._01_index.SecFullIndexFilePostProcessing import SecFullIndexFilePostProcessor
from secdaily._01_index.SecFullIndexFileProcessing import SecFullIndexFileProcessor
from secdaily._02_xml.db.XmlFileDownloadingDataAccess import XmlFileDownloadingDA
from secdaily._02_xml.db.XmlFileParsingDataAccess import XmlFileParsingDA
from secdaily._02_xml.db.XmlFilePreProcessingDataAccess import XmlFilePreProcessingDA
from secdaily._02_xml.SecXmlFileDownloading import SecXmlFileDownloader
from secdaily._02_xml.SecXmlFileParsing import SecXmlParser
from secdaily._02_xml.SecXmlFilePreProcessing import SecXmlFilePreprocessor
from secdaily._03_secstyle.db.SecStyleFormatterDataAccess import SecStyleFormatterDA
from secdaily._03_secstyle.SECStyleFormatting import SECStyleFormatter
from secdaily._04_dailyzip.DailyZipCreating import DailyZipCreator
from secdaily._04_dailyzip.db.DailyZipCreatingDataAccess import DailyZipCreatingDA


class SecDataOrchestrator:

    def __init__(
        self, workdir: str, user_agent_def: str, start_year: Optional[int] = None, start_qrtr: Optional[int] = None
    ):
        """
        :param user_agent_def: according to https://www.sec.gov/os/accessing-edgar-data in the
          form User-Agent: Sample Company Name AdminContact@<sample company domain>.com
        """

        if workdir[-1] != "/":
            workdir = workdir + "/"

        self.workdir = workdir
        self.xmldir = workdir + "_1_xml/"
        self.csvdir = workdir + "_2_csv/"
        self.formatdir = workdir + "_3_secstyle/"
        self.dailyzipdir = workdir + "_4_daily/"

        self.today = datetime.today()

        self.urldownloader = UrlDownloader(user_agent_def)

        if start_year is None:
            self.start_year = self.today.year
            self.start_qrtr = MONTH_TO_QRTR[self.today.month]
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

    def _log_main_header(self, title: str):
        logging.info("==============================================================")
        logging.info(title)
        logging.info("==============================================================")

    def _log_sub_header(self, title: str):
        logging.info("")
        logging.info("--------------------------------------------------------------")
        logging.info(title)
        logging.info("--------------------------------------------------------------")

    def _download_index_data(self):
        self._log_sub_header("looking for new reports")
        secfullindexprocessor = SecFullIndexFileProcessor(
            IndexProcessingDA(self.workdir), self.urldownloader, self.start_year, self.start_qrtr
        )
        secfullindexprocessor.process()

    def _postprocess_index_data(self):
        self._log_sub_header("add xbrl file urls")
        secfullindexpostprocessor = SecFullIndexFilePostProcessor(
            IndexPostProcessingDA(self.workdir), self.urldownloader
        )
        secfullindexpostprocessor.process()
        self._log_sub_header("check for duplicates")
        secfullindexpostprocessor.check_for_duplicated()

    def process_index_data(self):
        self._log_main_header("Process xbrl full index files")
        self._download_index_data()
        self._postprocess_index_data()

    def _preprocess_xml(self):
        self._log_sub_header("preprocess xml files")
        secxmlfilepreprocessor = SecXmlFilePreprocessor(XmlFilePreProcessingDA(self.workdir))
        secxmlfilepreprocessor.copy_entries_to_processing_table()

    def _download_xml(self):
        secxmlfilesdownloader = SecXmlFileDownloader(
            XmlFileDownloadingDA(self.workdir), self.urldownloader, self.xmldir
        )
        self._log_sub_header("download lab xml files")
        secxmlfilesdownloader.downloadLabFiles()

        self._log_sub_header("download num xml files")
        secxmlfilesdownloader.downloadNumFiles()

        self._log_sub_header("download pre xml files")
        secxmlfilesdownloader.downloadPreFiles()

    def _parse_xml(self):
        secxmlfileparser = SecXmlParser(XmlFileParsingDA(self.workdir), self.csvdir)
        self._log_sub_header("parse lab xml files")
        secxmlfileparser.parseLabFiles()

        self._log_sub_header("parse num xml files")
        secxmlfileparser.parseNumFiles()

        self._log_sub_header("parse pre xml files")
        secxmlfileparser.parsePreFiles()

    def process_xml_data(self):
        self._log_main_header("Process xbrl data files")
        self._preprocess_xml()
        self._download_xml()
        self._parse_xml()

    def create_sec_style(self):
        self._log_sub_header("create sec style files")
        formatter = SECStyleFormatter(dbmanager=SecStyleFormatterDA(self.workdir), data_dir=self.formatdir)
        formatter.process()

    def create_daily_zip(self):
        self._log_main_header("Create daily zip files")
        zip_creator = DailyZipCreator(DailyZipCreatingDA(self.workdir), self.dailyzipdir)
        zip_creator.process()

    def process(self):
        self.process_index_data()
        self.process_xml_data()
        self.create_sec_style()
        self.create_daily_zip()


if __name__ == "__main__":
    workdir_default = "d:/secprocessing2/"

    from secdaily._00_common.DBBase import DB

    DB(workdir_default).create_db()

    orchestrator = SecDataOrchestrator(
        workdir=workdir_default,
        user_agent_def="private user somebody.lastname@gmail.com",
        start_year=2024,
        start_qrtr=4,
    )
    orchestrator.process()
