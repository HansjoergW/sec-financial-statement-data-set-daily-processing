from _00_common.DBManagement import DBManager
from _00_common.SecFileUtils import download_url_to_file

import logging
import datetime
import os

from typing import List,Tuple,Callable
from time import time, sleep
from multiprocessing import Pool

class SecXmlFileProcessor:
    """
    - downloads the desired sec files, parses them and adds the information into the db.
    """

    def __init__(self, dbmanager: DBManager, xml_dir: str = "./tmp/xml/"):
        self.dbmanager = dbmanager
        self.processdate = datetime.date.today().isoformat()

        if xml_dir[-1] != '/':
            xml_dir = xml_dir + '/'

        self.xml_dir = xml_dir + self.processdate + '/'

        if not os.path.isdir(self.xml_dir):
            os.makedirs(self.xml_dir)


    @staticmethod
    def _download_file(data_tuple: Tuple[str]) -> (str, str):
        accessionnr = data_tuple[0]
        url = data_tuple[1]
        xml_dir = data_tuple[2]
        filename = url.rsplit('/', 1)[-1]

        filepath = xml_dir + filename
        try:
            download_url_to_file(url, filepath)
            return (filepath, accessionnr)
        except:
            logging.warning("failed to download from: " + url)
            print("failed download: ", url)
            return (None, accessionnr)

    @staticmethod
    def _download_file_throttle(data_tuple: Tuple[str]) -> (str, str):
        # ensures that only one request per second is send
        start = time()
        accession_nr, filename = SecXmlFileProcessor._download_file(data_tuple)
        end = time()
        sleep((1000-(end - start)) / 1000)
        return accession_nr, filename

    def _download(self, select_funct: Callable, update_funct: Callable):
        pool = Pool(8)
        missing:List[Tuple[str]] = select_funct()
        missing = [(*entry, self.xml_dir) for entry in missing]

        last_missing:int = None

        # we have to expect temporary problems, like restricted access or failed access
        # therefore this loop is used to repeatedly download files until all files could be downloaded
        # or no new files could be downloaded
        while (last_missing is None) or (last_missing > len(missing)):
            last_missing = len(missing)
            logging.info("missing entries " + str(len(missing)))

            for i in range(0, len(missing), 100):
                chunk = missing[i:i + 100]

                update_data: List[Tuple[str]] = pool.map(SecXmlFileProcessor._download_file_throttle, chunk)
                update_funct(update_data)

                logging.info("commited chunk: " + str(i))

            missing = select_funct()
            missing = [(*entry, self.xml_dir) for entry in missing]

        if len(missing) > 0:
            logging.info("Failed to add missing for " + str(len(missing)))

    def downloadNumFiles(self):
        self._download(self.dbmanager.find_missing_xmlNumFiles, self.dbmanager.update_processing_xml_num_file)

    def downloadPreFiles(self):
        self._download(self.dbmanager.find_missing_xmlPreFiles, self.dbmanager.update_processing_xml_pre_file)
