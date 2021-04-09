from _00_common.DBManagement import DBManager

from typing import List, Tuple
import requests
import logging
import re

from time import time, sleep
from multiprocessing import Pool

# Idee: verarbeiten der Daten in der DB, wenn sie mal dort, d.h. auch vervollständigen, etc.
# listet alle filenamen sauber
files = re.compile(r"\"name\":\"(.*?)\"", re.IGNORECASE + re.MULTILINE + re.DOTALL)


class SecFeedDataManager():

    def __init__(self, dbmanager: DBManager):
        self.dbmanager = dbmanager

    @staticmethod
    def _find_main_file(data_tuple: Tuple[str]) -> (str, str):
        pre_url = data_tuple[2]
        path = pre_url[0:pre_url.rfind("/")+1]

        json_file = path + "index.json"
        response = None
        current_try = 0
        while current_try < 4:
            current_try += 1
            try:
                response = requests.get(json_file, timeout=10)
                response.raise_for_status()
                break
            except requests.exceptions.RequestException as err:
                if current_try >= 4:
                    logging.exception("RequestException:%s", err)
                    return None, data_tuple[0]
                else:
                    logging.info("failed try " + str(current_try))
                    sleep(1)


        marks  = files.finditer(response.text)
        response.close()
        for mark in marks:
            if mark.groups()[0].endswith("htm.xml"):
                print("found for: " + path)
                new_url = path + mark.groups()[0]
                return new_url, data_tuple[0]
        return None, data_tuple[0]

    @staticmethod
    def _find_main_file_throttle(data_tuple: Tuple[str]) -> (str, str):
        # ensures that only one request per second is send
        start = time()
        new_url, accession_nr = SecFeedDataManager._find_main_file(data_tuple)
        end = time()
        sleep((1000-(end - start)) / 1000)
        return new_url, accession_nr

    def add_missing_xbrlinsurl(self):
        pool = Pool(8)

        last_missing:int = None
        missing: List[Tuple[str]] = self.dbmanager.find_missing_xbrl_ins_urls()
        while (last_missing is None) or (last_missing > len(missing)):
            last_missing = len(missing)
            logging.info("missing entries " + str(len(missing)))

            for i in range(0, len(missing), 100):
                chunk = missing[i:i + 100]
                update_data: List[Tuple[str]] = pool.map(SecFeedDataManager._find_main_file_throttle, chunk)
                self.dbmanager.update_xbrl_ins_urls(update_data)
                logging.info("commited chunk: " + str(i))

            missing = self.dbmanager.find_missing_xbrl_ins_urls()

        if len(missing) > 0:
            logging.info("Failed to addmissing for " + str(len(missing)))





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