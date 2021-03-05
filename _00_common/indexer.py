# https://github.com/robren/sec_edgar_download/blob/master/sec_edgar_download/indexer.py
"""This module provides functions to download and index edgar sec RSS
feeds and to download individual filers xbrl filings
:copyright: (c) 2017 by Robert Rennison
:license: Apache 2, see LICENCE for more details
"""

import os
import os.path
import sqlite3 as sqlite3
import logging
import pandas as pd
import requests
from bs4 import BeautifulSoup


def get_cik(ticker):
    """ Query the edgar site for the cik corresponding to a ticker.
    Returns a string representing the cik.
    By using the xml output format in the query and BeautifulSoup
    the parsing of the cik from the response is simple; avoiding
    the need for regexps
    """

    url = 'https://www.sec.gov/cgi-bin/browse-edgar'
    query_args = {'CIK': ticker, 'action': 'getcompany', 'output': 'xml'}
    response = requests.get(url, params=query_args)
    soup = BeautifulSoup(response.text, 'lxml')
    return soup.cik.get_text()


class SecIndexer():
    def __init__(self, work_dir="edgar/"):
        self.work_dir = work_dir
        self.database = os.path.join(self.work_dir, 'edgar.db')
        self.feed_dir = os.path.join(self.work_dir, 'rss-archives')
        self.filings_dir = os.path.join(self.work_dir, 'filings')

        self.edgar_keys = (
            'company_name', 'form_type', 'filing_date', 'cik_number',
            'accession_number', 'file_number', 'acceptance_datetime',
            'period', 'assistant_director', 'assigned_sic', 'fiscal_year_end',
            'xbrl_files'
        )

        self.edgar_add_keys = ('xbrl_cal_url', 'xbrl_def_url', 'xbrl_lab_url', 'xbrl_pre_url')

        self.edgar_all_keys = self.edgar_keys + self.edgar_add_keys

        self.edgar_labels = (
            'companyName', 'formType', 'filingDate', 'cikNumber',
            'accessionNumber', 'fileNumber', 'acceptanceDatetime',
            'period', 'assistantDirector', 'assignedSic', 'fiscalYearEnd',
            'xbrlFiles'
        )


        # FIXME, need to use a private logger not the root one.
        # logging.basicConfig(filename='logging.log',level=logging.DEBUG)
        logging.basicConfig(level=logging.INFO)

        self._prep_directories()
        self._prep_database_table()



    def download_xbrl_data(self, cik, from_year, to_year, form_type='All'):
        """Downloads xbrl filing data from the SEC edgar website
        Requires that the user has previously downloaded and indexed the feeds
        for the period in question using the CLI to invoke
        download_sec_feeds().  Downloads files to the subdirectory "filings"
        within the directory set by the work_dir class variable. This defaults
        to "./edgar" within the directory the application is running in.
        Args:
            cik (str): The SEC CIK number associatd with the filer.
            from_year (int): Beginning year to download filings from.
            to_year (int): Ending year for forms download.
            form_type (str: "10-K", "10-Q" or "All" (defaults to "All")
        """
        logging.debug('download_xbrl_data: cik = %s, form_type = %s,'
                      'from_year = %d, to_year = %d', cik, form_type,
                      from_year, to_year)

        conn = sqlite3.connect(self.database)
        df = pd.read_sql('SELECT * from feeds', conn)
        df.head()

        df['filing_date'] = pd.to_datetime(
            df['filing_date'],
            format='%m/%d/%Y')

        # TODO maybe allow from month and to month
        from_date = str(from_year) + '-01-01'
        to_date = str(to_year) + '-12-31'

        if form_type == 'All':
            mask = (df['filing_date'] >= from_date) \
                   & (df['filing_date'] <= to_date) \
                   & (df['cik_number'] == cik)

        else:
            mask = (df['filing_date'] >= from_date) \
                   & (df['filing_date'] <= to_date) \
                   & (df['cik_number'] == cik) \
                   & (df['form_type'] == form_type)

        masked_df = df.loc[mask]

        for url in masked_df['xbrl_files']:
            if url == None:
                print("no xbrl file found")
                continue
            print('Downloading file {}'.format(url))
            filename = os.path.join(self.filings_dir, os.path.basename(url))
            print('To {}'.format(filename))
            response = requests.get(url)
            with open(filename, 'w') as f:
                f.write(response.text)

                logging.debug('download_xbrl_data: found %d filings wrote to\
                        %s', len(masked_df), filename)
