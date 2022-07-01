import datetime
import logging
import os
from typing import Protocol, List

from _00_common.ParallelExecution import ParallelExecutor
from _00_common.SecFileUtils import download_url_to_file
from _02_xml.db.XmlFileDownloadingDataAccess import MissingFile


class DataAccessor(Protocol):

    def find_missing_xmlNumFiles(self) -> List[MissingFile]:
        """ find report entries in the process table for which the xml-num-file has not yet been downloaded """

    def find_missing_xmlPreFiles(self) -> List[MissingFile]:
        """ find report entries in the process table for which the xml-pre-file has not yet been downloaded """

    def update_processing_xml_num_file(self, update_list: List[MissingFile]):
        """ update the entry of a formerly missing xml-num-file and update it with the name of the downloaded file """

    def update_processing_xml_pre_file(self, update_list: List[MissingFile]):
        """ update the entry of a formerly missing xml-pre-file and update it with the name of the downloaded file """


class SecXmlFileDownloader:
    """
    - downloads the desired sec xml files, stores them and updates the sec-processing table
    """

    def __init__(self, dbmanager: DataAccessor, xml_dir: str = "./tmp/xml/"):
        self.dbmanager = dbmanager
        self.processdate = datetime.date.today().isoformat()

        if xml_dir[-1] != '/':
            xml_dir = xml_dir + '/'

        self.xml_dir = xml_dir + self.processdate + '/'

        if not os.path.isdir(self.xml_dir):
            os.makedirs(self.xml_dir)

    def _download_file(self, data: MissingFile) -> MissingFile:
        try:
            if data.fileSize is not None:
                size = int(data.fileSize)
            else:
                size = None
        except ValueError:
            size = None

        if data.url == None:
            logging.warning("url is null:  / " + data.accessionNumber)

        filename = data.url.rsplit('/', 1)[-1]

        filepath = self.xml_dir + data.accessionNumber + "-" + filename
        try:
            download_url_to_file(data.url, filepath, size)
            data.file = filepath
            return data
        except:
            logging.warning("failed to download from: " + data.url)
            return data

    def _download(self, executor: ParallelExecutor):
        _, missing = executor.execute()
        if len(missing) > 0:
            logging.info("   Failed to add missing for " + str(len(missing)))

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
