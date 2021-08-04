from _00_common.DBManagement import DBManager

from typing import List, Tuple
import requests
import logging
import json

from time import time, sleep
from multiprocessing import Pool

class SecIndexFilePostProcessor:
    """ earlier, it was common that the number xml was individual xml file which was also listed in the
    sec-feed file. However, today it is possible and gets more common that the number information is directly
    contained in the html itself. In these cases the sec does create the number xml file out of the html
     file (ending with htm.xm). However, this file does not appear in the IndexFile.
     Therefore it is necessary to get the index.json for a report and search for a file ending with
     htm.xml. This file is then the replacement for the old number xml ('xbrlInsUrl')"""

    def __init__(self, dbmanager: DBManager):
        self.dbmanager = dbmanager

    @staticmethod
    def _find_main_file(data_tuple: Tuple[str]) -> (str, str, str):
        pre_url = data_tuple[2]
        path = pre_url[0:pre_url.rfind("/")+1]

        json_file = path + "index.json"

        # todo: warum wird hier nicht die "normale" download Methode aus SecFileUtils verwendet?

        response = None
        current_try = 0
        while current_try < 4:
            current_try += 1
            try:
                response = requests.get(json_file, timeout=10, headers={'User-Agent': 'private user hansjoerg.wingeier@gmail.com'}, stream=True)
                response.raise_for_status()
                break
            except requests.exceptions.RequestException as err:
                if current_try >= 4:
                    logging.warning("failed to download from: {}".format(json_file))
                    return None, None, data_tuple[0]
                else:
                    logging.info("failed try " + str(current_try))
                    sleep(1)

        json_content = json.loads(response.text)

        response.close()
        itemlist:List = json_content['directory']['item']

        for item in itemlist:
            name = item['name']
            size = item['size']
            if name.endswith("htm.xml"):
                new_url = path + name
                return new_url, size, data_tuple[0]
        return None, None, data_tuple[0]

    @staticmethod
    def _find_main_file_throttle(data_tuple: Tuple[str]) -> (str, str):
        # ensures that only one request per second is send
        start = time()
        new_url, size, accession_nr = SecIndexFilePostProcessor._find_main_file(data_tuple)
        end = time()
        sleep((1000-(end - start)) / 1000)
        return new_url, size, accession_nr

    def add_missing_xbrlinsurl(self):
        pool = Pool(8)

        last_missing:int = None
        missing: List[Tuple[str]] = self.dbmanager.find_missing_xbrl_ins_urls()
        while (last_missing is None) or (last_missing > len(missing)):
            last_missing = len(missing)
            logging.info("missing entries " + str(len(missing)))

            for i in range(0, len(missing), 100):
                chunk = missing[i:i + 100]
                update_data: List[Tuple[str, str, str]] = pool.map(SecIndexFilePostProcessor._find_main_file_throttle, chunk)
                self.dbmanager.update_xbrl_ins_urls(update_data)
                logging.info("commited chunk: " + str(i))

            missing = self.dbmanager.find_missing_xbrl_ins_urls()

        if len(missing) > 0:
            logging.info("Failed to add missing for " + str(len(missing)))

    def check_for_duplicated(self):
        duplicated_adshs: List[str] = self.dbmanager.find_duplicated_adsh()
        for duplicated in duplicated_adshs:
            logging.info("Found duplicated: " + duplicated)
            self.dbmanager.mark_duplicated_adsh(duplicated)



    #     todo adding ticker with the help of
    #     def get_cik(ticker):
    # """ Query the edgar site for the cik corresponding to a ticker.
    # Returns a string representing the cik.
    # By using the xml output format in the query and BeautifulSoup
    # the parsing of the cik from the response is simple; avoiding
    # the need for regexps
    # """
    #
    # url = 'https://www.sec.gov/cgi-bin/browse-edgar'
    # query_args = {'CIK': ticker, 'action': 'getcompany', 'output': 'xml'}
    # response = requests.get(url, params=query_args)
    # soup = BeautifulSoup(response.text, 'lxml')
    # return soup.cik.get_text()