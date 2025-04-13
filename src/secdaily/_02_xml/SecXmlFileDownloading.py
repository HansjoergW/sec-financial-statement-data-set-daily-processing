import logging
import traceback
from typing import List, Protocol

from secdaily._00_common.DownloadUtils import UrlDownloader
from secdaily._00_common.ParallelExecution import ParallelExecutor
from secdaily._00_common.ProcessBase import ProcessBase
from secdaily._02_xml.db.XmlFileDownloadingDataAccess import MissingFile
from secdaily._02_xml.parsing.SecXmlParsingBase import ErrorEntry


class DataAccessor(Protocol):

    def find_missing_xmlNumFiles(self) -> List[MissingFile]:
        """find report entries in the process table for which the xml-num-file has not yet been downloaded"""
        return []

    def find_missing_xmlPreFiles(self) -> List[MissingFile]:
        """find report entries in the process table for which the xml-pre-file has not yet been downloaded"""
        return []

    def find_missing_xmlLabelFiles(self) -> List[MissingFile]:
        """find report entries in the process table for which the xml-lab-file has not yet been downloaded"""
        return []

    def update_processing_xml_num_file(self, update_list: List[MissingFile]):
        """update the entry of a formerly missing xml-num-file and update it with the name of the downloaded file"""

    def update_processing_xml_pre_file(self, update_list: List[MissingFile]):
        """update the entry of a formerly missing xml-pre-file and update it with the name of the downloaded file"""

    def update_processing_xml_label_file(self, update_list: List[MissingFile]):
        """update the entry of a formerly missing xml-lab-file and update it with the name of the downloaded file"""


class SecXmlFileDownloader(ProcessBase):
    """
    - downloads the desired sec xml files, stores them and updates the sec-processing table
    """

    def __init__(self, dbmanager: DataAccessor, urldownloader: UrlDownloader, data_dir: str = "./tmp/xml/"):
        super().__init__(data_dir=data_dir)

        self.dbmanager = dbmanager
        self.urldownloader = urldownloader

    def _download_file(self, data: MissingFile) -> MissingFile:
        try:
            if data.fileSize is not None:
                size = int(data.fileSize)
            else:
                size = None
        except ValueError:
            size = None

        if (data.url is None) | (data.url == ""):
            logging.warning("url is null: %s / %s ", data.accessionNumber, data.type)
            return data

        filename = data.url.rsplit("/", 1)[-1]

        filepath = self.data_path / data.get_qrtr_string() / data.get_filing_date() / filename

        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)

            self.urldownloader.download_url_to_file(data.url, str(filepath), size)
            data.file = str(filepath)
            return data
        except Exception as e: # pylint: disable=broad-except
            logging.warning("download for %s from %s failed: %s", data.accessionNumber, data.url, e)
            self._log_error(
                adsh=data.accessionNumber,
                file_type=f"download_failed_{data.type}",
                error_list=[ErrorEntry(adsh=data.accessionNumber, error_info=data.url, error=traceback.format_exc())],
            )

            return data

    def _download(self, executor: ParallelExecutor):
        _, missing = executor.execute()
        if len(missing) > 0:
            logging.info("   Failed to add missing for %s", str(len(missing)))

    def downloadNumFiles(self):
        logging.info("download Num Files")

        executor = ParallelExecutor[MissingFile, MissingFile, type(None)](max_calls_per_sec=8)
        executor.set_get_entries_function(self.dbmanager.find_missing_xmlNumFiles)
        executor.set_process_element_function(self._download_file)
        executor.set_post_process_chunk_function(self.dbmanager.update_processing_xml_num_file)
        self._download(executor)

    def downloadPreFiles(self):
        logging.info("download Pre Files")

        executor = ParallelExecutor[MissingFile, MissingFile, type(None)](max_calls_per_sec=8)
        executor.set_get_entries_function(self.dbmanager.find_missing_xmlPreFiles)
        executor.set_process_element_function(self._download_file)
        executor.set_post_process_chunk_function(self.dbmanager.update_processing_xml_pre_file)

        self._download(executor)

    def downloadLabFiles(self):
        logging.info("download Label Files")

        executor = ParallelExecutor[MissingFile, MissingFile, type(None)](max_calls_per_sec=8)
        executor.set_get_entries_function(self.dbmanager.find_missing_xmlLabelFiles)
        executor.set_process_element_function(self._download_file)
        executor.set_post_process_chunk_function(self.dbmanager.update_processing_xml_label_file)

        self._download(executor)
