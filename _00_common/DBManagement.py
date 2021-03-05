import os
import sqlite3
import re
from typing import List, Tuple
import pandas as pd

SEC_FEED_TBL_NAME = "sec_feeds"

SEC_FEED_TBL_COLS = (
    'companyName', 'formType', 'filingDate', 'cikNumber',
    'accessionNumber', 'fileNumber', 'acceptanceDatetime',
    'period', 'assistantDirector', 'assignedSic', 'fiscalYearEnd',
    'xbrlInsUrl', 'xbrlCalUrl', 'xbrlDefUrl', 'xbrlLabUrl', 'xbrlPreUrl'
)


class DBManager():

    def __init__(self, work_dir="edgar/"):
        self.work_dir = work_dir
        self.database = os.path.join(self.work_dir, 'sec_data.db')
        self._create_db()

    def _get_connection(self):
        return sqlite3.connect(self.database)

    def _create_db(self):
        """

        """
        if not os.path.isdir(self.work_dir):
            os.makedirs(self.work_dir)

        columns = ','.join(SEC_FEED_TBL_COLS)
        columns = re.sub('accessionNumber',
                         'accessionNumber PRIMARY KEY',
                         columns)

        table_parms = ('''CREATE TABLE IF NOT EXISTS {} ({})'''
                       .format(SEC_FEED_TBL_NAME, columns))

        conn = self._get_connection()
        curr = conn.cursor()
        curr.execute(table_parms)
        conn.commit()
        conn.close()

    def read_all(self) -> pd.DataFrame:
        conn = self._get_connection()
        try:
            sql = '''SELECT * FROM {}'''.format(SEC_FEED_TBL_NAME)
            return pd.read_sql_query(sql, conn)
        finally:
            conn.close()

    def insert_feed_info(self, df: pd.DataFrame):
        conn = self._get_connection()
        try:
            df.to_sql(SEC_FEED_TBL_NAME, conn, if_exists="replace", chunksize=1000)
        finally:
            conn.close()

    def find_missing_xbrl_ins_urls(self) -> List[Tuple[str]]:
        conn = self._get_connection()
        try:
            sql = '''SELECT accessionNumber, xbrl_ins_url, xbrl_pre_url FROM {} WHERE xbrl_ins_url is NULL'''.format(SEC_FEED_TBL_NAME)

            return conn.execute(sql).fetchall()
        finally:
            conn.close()

    def update_xbrl_ins_urls(self, update_data: List[Tuple[str]]):
        conn = self._get_connection()
        try:
            sql = '''UPDATE {} SET xbrl_ins_url = ? WHERE accession_number = ?'''.format(SEC_FEED_TBL_NAME)
            conn.executemany(sql, update_data)
            conn.commit()
        finally:
            conn.close()

