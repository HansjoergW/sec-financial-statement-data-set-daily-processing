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
        try:
            response = requests.get(json_file, timeout=4)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            logging.exception("RequestException:%s", err)

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
        missing: List[Tuple[str]] = self.dbmanager.find_missing_xbrl_ins_urls()

        pool = Pool(9)
        update_data: List[Tuple[str]] = pool.map(SecFeedDataManager._find_main_file_throttle, missing)
        self.dbmanager.update_xbrl_ins_urls(update_data)



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