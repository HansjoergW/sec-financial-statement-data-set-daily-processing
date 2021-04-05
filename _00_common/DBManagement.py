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
        # self._create_db()

    def _get_connection(self):
        return sqlite3.connect(self.database)

    # def _create_db(self):
    #     """
    #
    #     """
    #     if not os.path.isdir(self.work_dir):
    #         os.makedirs(self.work_dir)
    #
    #     columns = ','.join(SEC_FEED_TBL_COLS)
    #     columns = re.sub('accessionNumber',
    #                      'accessionNumber PRIMARY KEY',
    #                      columns)
    #
    #     table_parms = ('''CREATE TABLE IF NOT EXISTS {} ({})'''
    #                    .format(SEC_FEED_TBL_NAME, columns))
    #
    #     conn = self._get_connection()
    #     curr = conn.cursor()
    #     curr.execute(table_parms)
    #     conn.commit()
    #     conn.close()

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
            df.to_sql(SEC_FEED_TBL_NAME, conn, if_exists="append", chunksize=1000)
        finally:
            conn.close()

    def find_missing_xbrl_ins_urls(self) -> List[Tuple[str]]:
        conn = self._get_connection()
        try:
            sql = '''SELECT accessionNumber, xbrlInsUrl, xbrlPreUrl FROM {} WHERE xbrlInsUrl is NULL'''.format(
                SEC_FEED_TBL_NAME)

            return conn.execute(sql).fetchall()
        finally:
            conn.close()

    def update_xbrl_ins_urls(self, update_data: List[Tuple[str]]):
        conn = self._get_connection()
        try:
            sql = '''UPDATE {} SET xbrlInsUrl = ? WHERE accessionNumber = ?'''.format(SEC_FEED_TBL_NAME)
            conn.executemany(sql, update_data)
            conn.commit()
        finally:
            conn.close()

    def create_test_data(self):
        inserts = [
            "INSERT INTO sec_feeds ('accessionNumber', 'companyName', 'formType', 'filingDate', 'cikNumber', 'fileNumber', 'acceptanceDatetime', 'period', 'assistantDirector', 'assignedSic', 'fiscalYearEnd', 'xbrlCalUrl', 'xbrlDefUrl', 'xbrlLabUrl', 'xbrlPreUrl') VALUES ('0001437749-21-004277', 'COHU INC', '10-K', '02/26/2021', '0000021535', '001-04298', '20210226173215', '20201226', 'Office of Life Sciences', '3825', '1226', 'https://www.sec.gov/Archives/edgar/data/21535/000143774921004277/cohu-20201226_cal.xml', 'https://www.sec.gov/Archives/edgar/data/21535/000143774921004277/cohu-20201226_def.xml', 'https://www.sec.gov/Archives/edgar/data/21535/000143774921004277/cohu-20201226_lab.xml', 'https://www.sec.gov/Archives/edgar/data/21535/000143774921004277/cohu-20201226_pre.xml');",
            "INSERT INTO sec_feeds ('accessionNumber', 'companyName', 'formType', 'filingDate', 'cikNumber', 'fileNumber', 'acceptanceDatetime', 'period', 'assistantDirector', 'assignedSic', 'fiscalYearEnd', 'xbrlCalUrl', 'xbrlDefUrl', 'xbrlLabUrl', 'xbrlPreUrl') VALUES ('0001015328-21-000057', 'WINTRUST FINANCIAL CORP', '10-K', '02/26/2021', '0001015328', '001-35077', '20210226172958', '20201231', 'Office of Finance', '6022', '1231', 'https://www.sec.gov/Archives/edgar/data/1015328/000101532821000057/wtfc-20201231_cal.xml', 'https://www.sec.gov/Archives/edgar/data/1015328/000101532821000057/wtfc-20201231_def.xml', 'https://www.sec.gov/Archives/edgar/data/1015328/000101532821000057/wtfc-20201231_lab.xml', 'https://www.sec.gov/Archives/edgar/data/1015328/000101532821000057/wtfc-20201231_pre.xml');",
            "INSERT INTO sec_feeds ('accessionNumber', 'companyName', 'formType', 'filingDate', 'cikNumber', 'fileNumber', 'acceptanceDatetime', 'period', 'assistantDirector', 'assignedSic', 'fiscalYearEnd', 'xbrlCalUrl', 'xbrlDefUrl', 'xbrlLabUrl', 'xbrlPreUrl') VALUES ('0001654954-21-002132', 'UR-ENERGY INC', '10-K', '02/26/2021', '0001375205', '001-33905', '20210226172939', '20201231', 'Office of Energy & Transportation', '1040', '1231', 'https://www.sec.gov/Archives/edgar/data/1375205/000165495421002132/urg-20201231_cal.xml', 'https://www.sec.gov/Archives/edgar/data/1375205/000165495421002132/urg-20201231_def.xml', 'https://www.sec.gov/Archives/edgar/data/1375205/000165495421002132/urg-20201231_lab.xml', 'https://www.sec.gov/Archives/edgar/data/1375205/000165495421002132/urg-20201231_pre.xml');",
            "INSERT INTO sec_feeds ('accessionNumber', 'companyName', 'formType', 'filingDate', 'cikNumber', 'fileNumber', 'acceptanceDatetime', 'period', 'assistantDirector', 'assignedSic', 'fiscalYearEnd', 'xbrlCalUrl', 'xbrlDefUrl', 'xbrlLabUrl', 'xbrlPreUrl') VALUES ('0000073756-21-000023', 'OCEANEERING INTERNATIONAL INC', '10-K', '02/26/2021', '0000073756', '001-10945', '20210226172622', '20201231', 'Office of Energy & Transportation', '1389', '1231', 'https://www.sec.gov/Archives/edgar/data/73756/000007375621000023/oii-20201231_cal.xml', 'https://www.sec.gov/Archives/edgar/data/73756/000007375621000023/oii-20201231_def.xml', 'https://www.sec.gov/Archives/edgar/data/73756/000007375621000023/oii-20201231_lab.xml', 'https://www.sec.gov/Archives/edgar/data/73756/000007375621000023/oii-20201231_pre.xml');",
            "INSERT INTO sec_feeds ('accessionNumber', 'companyName', 'formType', 'filingDate', 'cikNumber', 'fileNumber', 'acceptanceDatetime', 'period', 'assistantDirector', 'assignedSic', 'fiscalYearEnd', 'xbrlCalUrl', 'xbrlDefUrl', 'xbrlLabUrl', 'xbrlPreUrl') VALUES ('0001564590-21-009508', 'Ceridian HCM Holding Inc.', '10-K', '02/26/2021', '0001725057', '001-38467', '20210226172344', '20201231', 'Office of Technology', '7372', '1231', 'https://www.sec.gov/Archives/edgar/data/1725057/000156459021009508/cday-20201231_cal.xml', 'https://www.sec.gov/Archives/edgar/data/1725057/000156459021009508/cday-20201231_def.xml', 'https://www.sec.gov/Archives/edgar/data/1725057/000156459021009508/cday-20201231_lab.xml', 'https://www.sec.gov/Archives/edgar/data/1725057/000156459021009508/cday-20201231_pre.xml');",
            "INSERT INTO sec_feeds ('accessionNumber', 'companyName', 'formType', 'filingDate', 'cikNumber', 'fileNumber', 'acceptanceDatetime', 'period', 'assistantDirector', 'assignedSic', 'fiscalYearEnd', 'xbrlCalUrl', 'xbrlDefUrl', 'xbrlLabUrl', 'xbrlPreUrl') VALUES ('0001273685-21-000032', 'NEW YORK MORTGAGE TRUST INC', '10-K', '02/26/2021', '0001273685', '001-32216', '20210226172340', '20201231', 'Office of Real Estate & Construction', '6798', '1231', 'https://www.sec.gov/Archives/edgar/data/1273685/000127368521000032/nymt-20201231_cal.xml', 'https://www.sec.gov/Archives/edgar/data/1273685/000127368521000032/nymt-20201231_def.xml', 'https://www.sec.gov/Archives/edgar/data/1273685/000127368521000032/nymt-20201231_lab.xml', 'https://www.sec.gov/Archives/edgar/data/1273685/000127368521000032/nymt-20201231_pre.xml');",
            "INSERT INTO sec_feeds ('accessionNumber', 'companyName', 'formType', 'filingDate', 'cikNumber', 'fileNumber', 'acceptanceDatetime', 'period', 'assistantDirector', 'assignedSic', 'fiscalYearEnd', 'xbrlCalUrl', 'xbrlDefUrl', 'xbrlLabUrl', 'xbrlPreUrl') VALUES ('0001564590-21-009507', 'Gores Holdings V Inc.', '10-K', '02/26/2021', '0001816816', '001-39429', '20210226172257', '20201231', 'Office of Real Estate & Construction', '6770', '1231', 'https://www.sec.gov/Archives/edgar/data/1816816/000156459021009507/grsv-20201231_cal.xml', 'https://www.sec.gov/Archives/edgar/data/1816816/000156459021009507/grsv-20201231_def.xml', 'https://www.sec.gov/Archives/edgar/data/1816816/000156459021009507/grsv-20201231_lab.xml', 'https://www.sec.gov/Archives/edgar/data/1816816/000156459021009507/grsv-20201231_pre.xml');"
        ]

        conn = self._get_connection()
        try:
            for sql in inserts:
                conn.execute(sql)
            conn.commit()
        finally:
            conn.close()