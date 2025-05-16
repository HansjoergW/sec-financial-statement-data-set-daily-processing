"""
Main module for the SEC Daily processing pipeline. Provides the Configuration class and SecDailyOrchestrator
that orchestrates the entire process of downloading, parsing, and creating SEC financial statement datasets.
"""

import logging
import random
from datetime import datetime
from typing import Optional

from secdaily._00_common.BaseDefinitions import QuarterInfo
from secdaily._00_common.DBBase import DB
from secdaily._00_common.DownloadUtils import UrlDownloader
from secdaily._00_common.Sponsoring import print_sponsoring_message
from secdaily._00_common.Version import print_newer_version_message
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
from secdaily._05_quarterzip.QuarterZipCreating import QuarterZipCreator
from secdaily._06_cleanup.Housekeeping import Housekeeper


class Configuration:
    """
    Configuration class for SecDailyOrchestrator.

    This class holds all the configuration parameters needed for the SEC data processing pipeline,
    including directory paths, user agent information, and cleanup flags.
    """

    # pylint: disable=line-too-long
    def __init__(
        self,
        user_agent_def: Optional[str] = None,
        workdir: Optional[str] = None,
        xmldir: Optional[str] = None,
        csvdir: Optional[str] = None,
        formatdir: Optional[str] = None,
        dailyzipdir: Optional[str] = None,
        quarterzipdir: Optional[str] = None,
        clean_intermediate_files: bool = False,
        clean_db_entries: bool = False,
        clean_daily_zip_files: bool = False,
        clean_quarter_zip_files: bool = False,
    ):
        """
        Initialize the Configuration object.

        Args:
            user_agent_def (Optional[str]): User agent string for SEC.gov requests. If not provided, a default string will be generated.
            workdir (Optional[str]): Working directory for storing all data. Defaults to current directory.
            xmldir (Optional[str]): Directory for storing XML files. If not provided, defaults to '_1_xml/' under workdir.
            csvdir (Optional[str]): Directory for storing CSV files. If not provided, defaults to '_2_csv/' under workdir.
            formatdir (Optional[str]): Directory for storing SEC-style formatted files. If not provided, defaults to '_3_secstyle/' under workdir.
            dailyzipdir (Optional[str]): Directory for storing daily zip files. If not provided, defaults to '_4_daily/' under workdir.
            quarterzipdir (Optional[str]): Directory for storing quarterly zip files. If not provided, defaults to '_5_quarter/' under workdir.
            clean_intermediate_files (bool): Flag to clean up intermediate files during housekeeping. Defaults to False.
            clean_db_entries (bool): Flag to clean up database entries during housekeeping. Defaults to False.
            clean_daily_zip_files (bool): Flag to clean up daily zip files during housekeeping. Defaults to False.
            clean_quarter_zip_files (bool): Flag to clean up quarterly zip files during housekeeping. Defaults to False.
        """
        self.user_agent_def = user_agent_def or f"private user somebody{random.randint(1, 1000)}.lastname@gmail.com"

        self.workdir = workdir or "./"
        if self.workdir[-1] != "/":
            self.workdir = self.workdir + "/"

        self.xmldir = xmldir or self.workdir + "_1_xml/"
        self.csvdir = csvdir or self.workdir + "_2_csv/"
        self.formatdir = formatdir or self.workdir + "_3_secstyle/"
        self.dailyzipdir = dailyzipdir or self.workdir + "_4_daily/"
        self.quarterzipdir = quarterzipdir or self.workdir + "_5_quarter/"

        self.clean_intermediate_files = clean_intermediate_files
        self.clean_db_entries = clean_db_entries
        self.clean_daily_zip_files = clean_daily_zip_files
        self.clean_quarter_zip_files = clean_quarter_zip_files


class SecDailyOrchestrator:

    def __init__(self, configuration: Configuration):
        """
        :param user_agent_def: according to https://www.sec.gov/os/accessing-edgar-data in the
          form User-Agent: Sample Company Name AdminContact@<sample company domain>.com
        """
        self.configuration = configuration

        DB(self.configuration.workdir).create_db()  # create database if ncessary

        self.today = datetime.today()

        self.urldownloader = UrlDownloader(self.configuration.user_agent_def)

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

    def _download_index_data(self, start_qrtr_info: QuarterInfo):
        self._log_sub_header("looking for new reports")
        secfullindexprocessor = SecFullIndexFileProcessor(
            dbmanager=IndexProcessingDA(self.configuration.workdir),
            urldownloader=self.urldownloader,
            start_year=start_qrtr_info.year,
            start_qrtr=start_qrtr_info.qrtr,
        )
        secfullindexprocessor.process()

    def _postprocess_index_data(self):
        self._log_sub_header("add xbrl file urls")
        secfullindexpostprocessor = SecFullIndexFilePostProcessor(
            IndexPostProcessingDA(self.configuration.workdir), self.urldownloader
        )
        secfullindexpostprocessor.process()
        self._log_sub_header("check for duplicates")
        secfullindexpostprocessor.check_for_duplicated()

    def process_index_data(self, start_qrtr_info: QuarterInfo):
        self._log_main_header("Process xbrl full index files")
        self._download_index_data(start_qrtr_info=start_qrtr_info)
        self._postprocess_index_data()

    def _preprocess_xml(self):
        self._log_sub_header("preprocess xml files")
        secxmlfilepreprocessor = SecXmlFilePreprocessor(XmlFilePreProcessingDA(self.configuration.workdir))
        secxmlfilepreprocessor.copy_entries_to_processing_table()

    def _download_xml(self):
        secxmlfilesdownloader = SecXmlFileDownloader(
            XmlFileDownloadingDA(self.configuration.workdir), self.urldownloader, self.configuration.xmldir
        )
        self._log_sub_header("download lab xml files")
        secxmlfilesdownloader.downloadLabFiles()

        self._log_sub_header("download num xml files")
        secxmlfilesdownloader.downloadNumFiles()

        self._log_sub_header("download pre xml files")
        secxmlfilesdownloader.downloadPreFiles()

    def _parse_xml(self):
        secxmlfileparser = SecXmlParser(XmlFileParsingDA(self.configuration.workdir), self.configuration.csvdir)
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
        formatter = SECStyleFormatter(
            dbmanager=SecStyleFormatterDA(self.configuration.workdir), data_dir=self.configuration.formatdir
        )
        formatter.process()

    def create_daily_zip(self):
        self._log_main_header("Create daily zip files")
        zip_creator = DailyZipCreator(DailyZipCreatingDA(self.configuration.workdir), self.configuration.dailyzipdir)
        zip_creator.process()

    def create_quarter_zip(self, start_qrtr_info: QuarterInfo):
        self._log_main_header("Create quarter zip files")
        quarter_zip_creator = QuarterZipCreator(
            start_qrtr_info=start_qrtr_info,
            daily_zip_dir=self.configuration.dailyzipdir,
            quarter_zip_dir=self.configuration.quarterzipdir,
        )
        quarter_zip_creator.process()

    def housekeeping(self, start_qrtr_info: QuarterInfo):
        self._log_main_header("Housekeeping")
        housekeeper = Housekeeper(
            start_qrtr_info=start_qrtr_info,
            xml_dir=self.configuration.xmldir,
            csv_dir=self.configuration.csvdir,
            secstyle_dir=self.configuration.formatdir,
            daily_zip_dir=self.configuration.dailyzipdir,
            quarter_zip_dir=self.configuration.quarterzipdir,
            work_dir=self.configuration.workdir,
        )

        housekeeper.process(
            remove_processing_files=self.configuration.clean_intermediate_files,
            remove_db_entries=self.configuration.clean_db_entries,
            remove_daily_zip_files=self.configuration.clean_daily_zip_files,
            remove_quarter_zip_files=self.configuration.clean_quarter_zip_files,
        )

    def process(self, start_year: Optional[int] = None, start_qrtr: Optional[int] = None):
        start_qrtr_info = QuarterInfo(year=start_year, qrtr=start_qrtr)

        self.process_index_data(start_qrtr_info=start_qrtr_info)
        self.process_xml_data()
        self.create_sec_style()
        self.create_daily_zip()
        self.create_quarter_zip(start_qrtr_info=start_qrtr_info)

        self.housekeeping(start_qrtr_info=start_qrtr_info)

        print_sponsoring_message()
        print_newer_version_message()
