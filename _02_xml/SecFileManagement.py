import os
import logging
import requests
import pandas as pd
from lxml import etree
from typing import List, Dict


FEED_FIELDS = (
    'companyName', 'formType', 'filingDate', 'cikNumber',
    'accessionNumber', 'fileNumber', 'acceptanceDatetime',
    'period', 'assistantDirector', 'assignedSic', 'fiscalYearEnd', 'xbrlFiles')

XBRL_FILE_FIELDS = ('xbrlInsUrl', 'xbrlCalUrl', 'xbrlDefUrl', 'xbrlLabUrl', 'xbrlPreUrl')

# DATA_COLS = list(FEED_FIELDS + XBRL_FILE_FIELDS)
# DATA_COLS.remove('xbrlFiles')
# DATA_COLS = tuple(DATA_COLS)


class SecIndexFile():
    """ inspired from # https://github.com/robren/sec_edgar_download/blob/master/sec_edgar_download/indexer.py
    downloads the file for the configured year and month
    parses the data and returns a pandas dataframe with all 10-K and 10-Q entries in this year/month
    """

    namespace = "https://www.sec.gov/Archives/edgar"

    """ reads the index file of the provided month and year and returns the data as pandas dataframe"""

    def __init__(self, year: int, month: int, feed_dir: str = "./tmp/"):
        self.year = year
        self.month = month
        self.feed_dir = feed_dir

        self.feed_filename = ('xbrlrss-' + str(self.year) + '-' + '{:02}'.format(self.month) + '.xml')
        logging.debug('feed_filename = %s', self.feed_filename)

        self.feed_file = os.path.join(feed_dir, self.feed_filename)

    def download_sec_feed(self):
        """Download an SEC RSS feed for a specifc month of a given year
        Downloads RSS feeds from the SEC edgar website for a given year and
        month.  The feeds are stored by year and month, each containing
        details of all of the filings made to the SEC for that month
        Returns:
            feed_file (str): The location of the downloaded RSS file.
        """
        logging.debug('download_sec_feed: year = %d, month = %d', self.year, self.month)

        if not os.path.isdir(self.feed_dir):
            os.makedirs(self.feed_dir)

        edgar_filings_feed = (self.namespace + '/monthly/' + self.feed_filename)
        logging.debug('Edgar Filings Feed = %s', edgar_filings_feed)

        response = None
        try:
            response = requests.get(edgar_filings_feed, timeout=4)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            logging.exception("RequestException:%s", err)
            return

        with open(self.feed_file, 'w') as file:
            file.write(response.text)

        logging.info('Downloaded RSS feed: %s', self.feed_file)

    def _parse_xbrlfiles(self, edgar_sub_elem: etree.Element, edgar_ns: Dict[str, str]):

        ed_xbrl = './/edgar:xbrlFile'
        xbrl_files = edgar_sub_elem.findall(ed_xbrl, namespaces=edgar_ns)

        xbrl_ins_url = None
        xbrl_cal_url = None
        xbrl_def_url = None
        xbrl_lab_url = None
        xbrl_pre_url = None

        for xbrl_file in xbrl_files:
            xbrl_type = xbrl_file.attrib['{' + self.namespace + '}type']

            if xbrl_type == "EX-101.INS" or xbrl_type == 'EX-100.INS':
                xbrl_ins_url = xbrl_file.attrib['{' + self.namespace + '}url']

            if xbrl_type == "EX-101.CAL" or xbrl_type == 'EX-100.CAL':
                xbrl_cal_url = xbrl_file.attrib['{' + self.namespace + '}url']

            if xbrl_type == "EX-101.DEF" or xbrl_type == 'EX-100.DEF':
                xbrl_def_url = xbrl_file.attrib['{' + self.namespace + '}url']

            if xbrl_type == "EX-101.LAB" or xbrl_type == 'EX-100.LAB':
                xbrl_lab_url = xbrl_file.attrib['{' + self.namespace + '}url']

            if xbrl_type == "EX-101.PRE" or xbrl_type == 'EX-100.PRE':
                xbrl_pre_url = xbrl_file.attrib['{' + self.namespace + '}url']

        return xbrl_ins_url, xbrl_cal_url, xbrl_def_url, xbrl_lab_url, xbrl_pre_url

    def parse_sec_rss_feeds(self) -> pd.DataFrame:
        """ Parses an Edgar RSS feed into a dict
        """
        logging.info("Parsing RSS feed %s", self.feed_file)

        root = etree.parse(self.feed_file).getroot()
        # 'items' elements contain the filing details for each company listed
        items = list(root.iter('item'))
        logging.debug('%d items found in RSS feed', len(items))

        edgar_ns = {'edgar': self.namespace}
        entries = []

        for item in items:
            temp_dict = {}

            for key in FEED_FIELDS:
                edgar_sub_elem = item.find('.//edgar:' + key, namespaces=edgar_ns)
                if edgar_sub_elem is None:
                    temp_dict[key] = None
                    continue

                # xbrlfiles contains the URLs of the actual filings
                if 'xbrlFiles' in edgar_sub_elem.tag:
                    assert key == 'xbrlFiles'
                    xbrl_ins_url, xbrl_cal_url, xbrl_def_url, xbrl_lab_url, xbrl_pre_url = self._parse_xbrlfiles(
                        edgar_sub_elem, edgar_ns)

                    # edgar_dict[key].append(xbrl_url)
                    temp_dict['xbrlInsUrl'] = xbrl_ins_url
                    temp_dict['xbrlCalUrl'] = xbrl_cal_url
                    temp_dict['xbrlDefUrl'] = xbrl_def_url
                    temp_dict['xbrlLabUrl'] = xbrl_lab_url
                    temp_dict['xbrlPreUrl'] = xbrl_pre_url

                else:
                    temp_dict[key] = edgar_sub_elem.text

            if temp_dict['formType'] in ['10-K', '10-Q']:  # we are only interested in 10-K and 10-Q reports
                entries.append(temp_dict)

        df = pd.DataFrame(entries)

        len_before = len(df)
        df.drop_duplicates('accessionNumber', inplace=True)
        len_after = len(df)
        dropped = len_before - len_after
        if dropped:
            logging.info('Dropped %d duplicates', dropped)

        return df
