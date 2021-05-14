from _00_common.SecFileUtils import download_url_to_file

import os
import logging
import pandas as pd
from lxml import etree
from typing import Dict, Tuple

FEED_FIELDS = (
    'companyName', 'formType', 'filingDate', 'cikNumber',
    'accessionNumber', 'fileNumber', 'acceptanceDatetime',
    'period', 'assistantDirector', 'assignedSic', 'fiscalYearEnd', 'xbrlFiles')

XBRL_FILE_FIELDS = ('xbrlInsUrl', 'xbrlCalUrl', 'xbrlDefUrl', 'xbrlLabUrl', 'xbrlPreUrl')


class SecIndexFileParser():
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

        edgar_filings_feed = (self.namespace + '/monthly/' + self.feed_filename)
        logging.debug('Edgar Filings Feed = %s', edgar_filings_feed)

        if not os.path.isdir(self.feed_dir):
            os.makedirs(self.feed_dir)

        download_url_to_file(edgar_filings_feed, self.feed_file)

        logging.info('Downloaded RSS feed: %s', self.feed_file)

    def _parse_xbrlfiles(self, edgar_sub_elem: etree.Element, edgar_ns: Dict[str, str]) -> Tuple[str]:

        ed_xbrl = './/edgar:xbrlFile'
        xbrl_files = edgar_sub_elem.findall(ed_xbrl, namespaces=edgar_ns)

        xbrl_ins_url = None
        xbrl_cal_url = None
        xbrl_def_url = None
        xbrl_lab_url = None
        xbrl_pre_url = None
        xbrl_ins_size = None
        xbrl_cal_size = None
        xbrl_def_size = None
        xbrl_lab_size = None
        xbrl_pre_size = None
        xbrl_ins_lastchanged = None
        xbrl_cal_lastchanged = None
        xbrl_def_lastchanged = None
        xbrl_lab_lastchanged = None
        xbrl_pre_lastchanged = None

        for xbrl_file in xbrl_files:
            xbrl_type = xbrl_file.attrib['{' + self.namespace + '}type']

            if xbrl_type == "EX-101.INS" or xbrl_type == 'EX-100.INS':
                xbrl_ins_url = xbrl_file.attrib['{' + self.namespace + '}url']
                xbrl_ins_size = xbrl_file.attrib['{' + self.namespace + '}size']

            if xbrl_type == "EX-101.CAL" or xbrl_type == 'EX-100.CAL':
                xbrl_cal_url = xbrl_file.attrib['{' + self.namespace + '}url']
                xbrl_cal_size = xbrl_file.attrib['{' + self.namespace + '}size']

            if xbrl_type == "EX-101.DEF" or xbrl_type == 'EX-100.DEF':
                xbrl_def_url = xbrl_file.attrib['{' + self.namespace + '}url']
                xbrl_def_size = xbrl_file.attrib['{' + self.namespace + '}size']

            if xbrl_type == "EX-101.LAB" or xbrl_type == 'EX-100.LAB':
                xbrl_lab_url = xbrl_file.attrib['{' + self.namespace + '}url']
                xbrl_lab_size = xbrl_file.attrib['{' + self.namespace + '}size']

            if xbrl_type == "EX-101.PRE" or xbrl_type == 'EX-100.PRE':
                xbrl_pre_url = xbrl_file.attrib['{' + self.namespace + '}url']
                xbrl_pre_size = xbrl_file.attrib['{' + self.namespace + '}size']

        return xbrl_ins_url, xbrl_cal_url, xbrl_def_url, xbrl_lab_url, xbrl_pre_url, \
               xbrl_ins_size, xbrl_cal_size, xbrl_def_size, xbrl_lab_size, xbrl_pre_size

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
                    xbrl_ins_url, xbrl_cal_url, xbrl_def_url, xbrl_lab_url, xbrl_pre_url, \
                    xbrl_ins_size, xbrl_cal_size, xbrl_def_size, xbrl_lab_size, xbrl_pre_size = self._parse_xbrlfiles(edgar_sub_elem, edgar_ns)

                    # edgar_dict[key].append(xbrl_url)
                    temp_dict['xbrlInsUrl'] = xbrl_ins_url
                    temp_dict['xbrlCalUrl'] = xbrl_cal_url
                    temp_dict['xbrlDefUrl'] = xbrl_def_url
                    temp_dict['xbrlLabUrl'] = xbrl_lab_url
                    temp_dict['xbrlPreUrl'] = xbrl_pre_url
                    temp_dict['insSize'] = xbrl_ins_size
                    temp_dict['calSize'] = xbrl_cal_size
                    temp_dict['defSize'] = xbrl_def_size
                    temp_dict['labSize'] = xbrl_lab_size
                    temp_dict['preSize'] = xbrl_pre_size

                else:
                    temp_dict[key] = edgar_sub_elem.text

            if temp_dict['formType'] in ['10-K', '10-Q']:  # we are only interested in 10-K and 10-Q reports
                entries.append(temp_dict)

        df = pd.DataFrame(entries)

        len_before = len(df)
        if len_before == 0:
            logging.info('empty feed file')
            return df

        df.drop_duplicates('accessionNumber', inplace=True)
        df.set_index('accessionNumber', inplace=True)
        len_after = len(df)
        dropped = len_before - len_after
        if dropped:
            logging.info('Dropped %d duplicates', dropped)

        df['sec_feed_file'] = self.feed_filename
        df['filingMonth'] = pd.to_numeric(df.filingDate.str.slice(0,2), downcast="integer")
        df['filingYear'] = pd.to_numeric(df.filingDate.str.slice(6,10), downcast="integer")

        return df