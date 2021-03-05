from _00_common.DBManagement import DBManager
from _02_xml.SecFileManagement import SecIndexFile

import requests
import logging
import re

from typing import List, Tuple
from time import time, sleep
from multiprocessing import Pool


# listet alle filenamen sauber
files = re.compile(r"\"name\":\"(.*?)\"", re.IGNORECASE + re.MULTILINE + re.DOTALL)

class SecFilesProcessor:
    """
    - downloads the desired sec files, parses them and adds the information into the db.
    - completes information for missing xbrl-Ins files
    - adding ticker?
    """

    def __init__(self, dbmanager: DBManager, start_year:int, end_year: int, start_month: int = 1, end_month:int = 12 ):
        self.dbmanager = dbmanager
        self.start_year = start_year
        self.end_year = end_year
        self.start_month = start_month
        self.end_month = end_month

    def _month_year_iter(self):
        ym_from = 12 * self.start_year + self.start_month - 1
        ym_to = 12 * self.end_year + self.end_month
        for yearm in range(ym_from, ym_to):
            year, month = divmod(yearm, 12)
            yield year, month + 1

    def download_sec_feeds(self):
        for year, month in self._month_year_iter():
            sec_file = SecIndexFile(year, month)
            sec_file.download_sec_feed()
            df = sec_file.parse_sec_rss_feeds()
            self.dbmanager.insert_feed_info(df)

    def _find_main_file(self, data_tuple: Tuple[str]) -> (str, str):
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

    def _find_main_file_throttle(self, data_tuple: Tuple[str]) -> (str, str):
        start = time()
        new_url, accession_nr = self._find_main_file(data_tuple)
        end = time()
        sleep((1000-(end - start)) / 1000)
        return new_url, accession_nr

    def add_missing_xbrlinsurl(self):
        missing: List[Tuple[str]] = self.dbmanager.find_missing_xbrl_ins_urls()

        pool = Pool(9)
        update_data = pool.map(self._find_main_file_throttle, missing)





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