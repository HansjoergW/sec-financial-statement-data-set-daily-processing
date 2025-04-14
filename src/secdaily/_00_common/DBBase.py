import glob
import os
import sqlite3
from abc import ABC
from typing import Dict, List, TypeVar

import pandas as pd

T = TypeVar("T")

CURRENT_DIR, CURRENT_FILE = os.path.split(__file__)
DDL_PATH = os.path.join(CURRENT_DIR, "sql")


# noinspection SqlResolve
# ruff: noqa: E501
# pylint: disable=line-too-long
class DB(ABC):
    """
    BaseClass für DB access to sqlite.
    It provides some basic functionality
    """

    SEC_REPORTS_TBL_NAME = "sec_reports"
    SEC_REPORT_PROCESSING_TBL_NAME = "sec_report_processing"
    SEC_FULL_INDEX_FILE_TBL_NAME = "sec_fullindex_file"
    MASS_TESTING_V2_TBL_NAME = "mass_testing_v2"

    TESTDATA_PATH = os.path.realpath(__file__ + "/..") + "/testdata/"

    def __init__(self, work_dir="edgar/"):
        self.work_dir = work_dir
        self.database = os.path.join(self.work_dir, "sec_processing.db")

    def get_connection(self):
        return sqlite3.connect(self.database)

    def create_db(self):
        sqlfiles = list(glob.glob(f"{DDL_PATH}/*.sql"))

        indexes_dict: Dict[int, str] = {}
        for sqlfilepath in sqlfiles:
            sqlfile = os.path.basename(sqlfilepath)

            index = int(sqlfile[sqlfile.rfind("\\V") + 2 : sqlfile.find("__")])
            indexes_dict[index] = sqlfilepath

        indexes = list(indexes_dict.keys())
        indexes.sort()

        if not os.path.isdir(self.work_dir):
            os.makedirs(self.work_dir)

        conn = self.get_connection()
        curr = conn.cursor()
        for index in indexes:
            sqlfile = indexes_dict[index]
            print(f"setup db: execute {sqlfile}")
            with open(sqlfile, "r", encoding="utf-8") as f:
                script = f.read()
                curr.executescript(script)
            conn.commit()
        conn.close()

    def _execute_read_as_df(self, sql: str) -> pd.DataFrame:
        conn = self.get_connection()
        try:
            return pd.read_sql_query(sql, conn)
        finally:
            conn.close()

    def _execute_single(self, sql: str):
        conn = self.get_connection()
        try:
            conn.execute(sql)
            conn.commit()
        finally:
            conn.close()

    def _execute_many(self, sql: str, params):
        conn = self.get_connection()
        try:
            conn.executemany(sql, params)
            conn.commit()
        finally:
            conn.close()

    def _execute_fetchall(self, sql: str) -> List[T]:
        conn = self.get_connection()
        try:
            return conn.execute(sql).fetchall()
        finally:
            conn.close()

    def _execute_fetchall_typed(self, sql, type_class: type[T]) -> List[T]:
        conn = self.get_connection()
        try:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute(sql)
            results = c.fetchall()
            return [type_class(**dict(x)) for x in results]
        finally:
            conn.close()

    def create_test_data(self):
        inserts = [
            "INSERT INTO sec_reports ('accessionNumber', 'companyName', 'formType', 'filingDate', 'cikNumber', 'fileNumber', 'acceptanceDatetime', 'period', 'assistantDirector', 'assignedSic', 'fiscalYearEnd', 'xbrlInsUrl', 'xbrlCalUrl', 'xbrlDefUrl', 'xbrlLabUrl', 'xbrlPreUrl','sec_feed_file') VALUES ('0001437749-21-004277', 'COHU INC', '10-K', '02/26/2021', '0000021535', '001-04298', '20210226173215', '20201226', 'Office of Life Sciences', '3825', '1226', 'https://www.sec.gov/Archives/edgar/data/21535/000143774921004277/cohu20201226_10k_htm.xml','https://www.sec.gov/Archives/edgar/data/21535/000143774921004277/cohu-20201226_cal.xml', 'https://www.sec.gov/Archives/edgar/data/21535/000143774921004277/cohu-20201226_def.xml', 'https://www.sec.gov/Archives/edgar/data/21535/000143774921004277/cohu-20201226_lab.xml', 'https://www.sec.gov/Archives/edgar/data/21535/000143774921004277/cohu-20201226_pre.xml','file1.xml');",
            "INSERT INTO sec_reports ('accessionNumber', 'companyName', 'formType', 'filingDate', 'cikNumber', 'fileNumber', 'acceptanceDatetime', 'period', 'assistantDirector', 'assignedSic', 'fiscalYearEnd', 'xbrlInsUrl', 'xbrlCalUrl', 'xbrlDefUrl', 'xbrlLabUrl', 'xbrlPreUrl','sec_feed_file') VALUES ('0001015328-21-000057', 'WINTRUST FINANCIAL CORP', '10-K', '02/26/2021', '0001015328', '001-35077', '20210226172958', '20201231', 'Office of Finance', '6022', '1231', 'https://www.sec.gov/Archives/edgar/data/1015328/000101532821000057/wtfc-20201231_htm.xml', 'https://www.sec.gov/Archives/edgar/data/1015328/000101532821000057/wtfc-20201231_cal.xml', 'https://www.sec.gov/Archives/edgar/data/1015328/000101532821000057/wtfc-20201231_def.xml', 'https://www.sec.gov/Archives/edgar/data/1015328/000101532821000057/wtfc-20201231_lab.xml', 'https://www.sec.gov/Archives/edgar/data/1015328/000101532821000057/wtfc-20201231_pre.xml','file1.xml');",
            "INSERT INTO sec_reports ('accessionNumber', 'companyName', 'formType', 'filingDate', 'cikNumber', 'fileNumber', 'acceptanceDatetime', 'period', 'assistantDirector', 'assignedSic', 'fiscalYearEnd', 'xbrlInsUrl', 'xbrlCalUrl', 'xbrlDefUrl', 'xbrlLabUrl', 'xbrlPreUrl','sec_feed_file') VALUES ('0001654954-21-002132', 'UR-ENERGY INC', '10-K', '02/26/2021', '0001375205', '001-33905', '20210226172939', '20201231', 'Office of Energy & Transportation', '1040', '1231', 'https://www.sec.gov/Archives/edgar/data/1375205/000165495421002132/urg_10k_htm.xml', 'https://www.sec.gov/Archives/edgar/data/1375205/000165495421002132/urg-20201231_cal.xml', 'https://www.sec.gov/Archives/edgar/data/1375205/000165495421002132/urg-20201231_def.xml', 'https://www.sec.gov/Archives/edgar/data/1375205/000165495421002132/urg-20201231_lab.xml', 'https://www.sec.gov/Archives/edgar/data/1375205/000165495421002132/urg-20201231_pre.xml','file1.xml');",
            "INSERT INTO sec_reports ('accessionNumber', 'companyName', 'formType', 'filingDate', 'cikNumber', 'fileNumber', 'acceptanceDatetime', 'period', 'assistantDirector', 'assignedSic', 'fiscalYearEnd', 'xbrlInsUrl', 'xbrlCalUrl', 'xbrlDefUrl', 'xbrlLabUrl', 'xbrlPreUrl','sec_feed_file') VALUES ('0000073756-21-000023', 'OCEANEERING INTERNATIONAL INC', '10-K', '02/26/2021', '0000073756', '001-10945', '20210226172622', '20201231', 'Office of Energy & Transportation', '1389', '1231', 'https://www.sec.gov/Archives/edgar/data/73756/000007375621000023/oii-20201231_htm.xml', 'https://www.sec.gov/Archives/edgar/data/73756/000007375621000023/oii-20201231_cal.xml', 'https://www.sec.gov/Archives/edgar/data/73756/000007375621000023/oii-20201231_def.xml', 'https://www.sec.gov/Archives/edgar/data/73756/000007375621000023/oii-20201231_lab.xml', 'https://www.sec.gov/Archives/edgar/data/73756/000007375621000023/oii-20201231_pre.xml','file1.xml');",
            "INSERT INTO sec_reports ('accessionNumber', 'companyName', 'formType', 'filingDate', 'cikNumber', 'fileNumber', 'acceptanceDatetime', 'period', 'assistantDirector', 'assignedSic', 'fiscalYearEnd', 'xbrlInsUrl', 'xbrlCalUrl', 'xbrlDefUrl', 'xbrlLabUrl', 'xbrlPreUrl','sec_feed_file') VALUES ('0001564590-21-009508', 'Ceridian HCM Holding Inc.', '10-K', '02/26/2021', '0001725057', '001-38467', '20210226172344', '20201231', 'Office of Technology', '7372', '1231', 'https://www.sec.gov/Archives/edgar/data/1725057/000156459021009508/cday-10k_20201231_htm.xml','https://www.sec.gov/Archives/edgar/data/1725057/000156459021009508/cday-20201231_cal.xml', 'https://www.sec.gov/Archives/edgar/data/1725057/000156459021009508/cday-20201231_def.xml', 'https://www.sec.gov/Archives/edgar/data/1725057/000156459021009508/cday-20201231_lab.xml', 'https://www.sec.gov/Archives/edgar/data/1725057/000156459021009508/cday-20201231_pre.xml','file1.xml');",
            "INSERT INTO sec_reports ('accessionNumber', 'companyName', 'formType', 'filingDate', 'cikNumber', 'fileNumber', 'acceptanceDatetime', 'period', 'assistantDirector', 'assignedSic', 'fiscalYearEnd', 'xbrlInsUrl', 'xbrlCalUrl', 'xbrlDefUrl', 'xbrlLabUrl', 'xbrlPreUrl','sec_feed_file') VALUES ('0001273685-21-000032', 'NEW YORK MORTGAGE TRUST INC', '10-K', '02/26/2021', '0001273685', '001-32216', '20210226172340', '20201231', 'Office of Real Estate & Construction', '6798', '1231', 'https://www.sec.gov/Archives/edgar/data/1273685/000127368521000032/nymt-20201231_htm.xml', 'https://www.sec.gov/Archives/edgar/data/1273685/000127368521000032/nymt-20201231_cal.xml', 'https://www.sec.gov/Archives/edgar/data/1273685/000127368521000032/nymt-20201231_def.xml', 'https://www.sec.gov/Archives/edgar/data/1273685/000127368521000032/nymt-20201231_lab.xml', 'https://www.sec.gov/Archives/edgar/data/1273685/000127368521000032/nymt-20201231_pre.xml','file1.xml');",
            "INSERT INTO sec_reports ('accessionNumber', 'companyName', 'formType', 'filingDate', 'cikNumber', 'fileNumber', 'acceptanceDatetime', 'period', 'assistantDirector', 'assignedSic', 'fiscalYearEnd', 'xbrlInsUrl', 'xbrlCalUrl', 'xbrlDefUrl', 'xbrlLabUrl', 'xbrlPreUrl','sec_feed_file') VALUES ('0001564590-21-009507', 'Gores Holdings V Inc.', '10-K', '02/26/2021', '0001816816', '001-39429', '20210226172257', '20201231', 'Office of Real Estate & Construction', '6770', '1231', 'https://www.sec.gov/Archives/edgar/data/1816816/000156459021009507/grsv-10k_20201231_htm.xml', 'https://www.sec.gov/Archives/edgar/data/1816816/000156459021009507/grsv-20201231_cal.xml', 'https://www.sec.gov/Archives/edgar/data/1816816/000156459021009507/grsv-20201231_def.xml', 'https://www.sec.gov/Archives/edgar/data/1816816/000156459021009507/grsv-20201231_lab.xml', 'https://www.sec.gov/Archives/edgar/data/1816816/000156459021009507/grsv-20201231_pre.xml','file1.xml');",
        ]

        conn = self.get_connection()
        try:
            for sql in inserts:
                conn.execute(sql)
            conn.commit()
        finally:
            conn.close()

    def create_processing_test_data(self):
        inserts = [
            f"INSERT INTO sec_report_processing ('accessionNumber', 'formType', 'filingDate', 'filingDay', 'filingMonth', 'filingYear', 'cikNumber', 'xbrlInsUrl', 'xbrlPreUrl', 'xmlNumFile', 'xmlPreFile') VALUES ('0001437749-21-004277', '10-K', '02/26/2021', 26, 2, 2021, '0000021535', 'https://www.sec.gov/Archives/edgar/data/21535/000143774921004277/cohu20201226_10k_htm.xml', 'https://www.sec.gov/Archives/edgar/data/21535/000143774921004277/cohu-20201226_pre.xml', '{self.TESTDATA_PATH}cohu20201226_10k_htm.xml', '{self.TESTDATA_PATH}cohu-20201226_pre.xml');",
            f"INSERT INTO sec_report_processing ('accessionNumber', 'formType', 'filingDate', 'filingDay', 'filingMonth', 'filingYear', 'cikNumber', 'xbrlInsUrl', 'xbrlPreUrl', 'xmlNumFile', 'xmlPreFile') VALUES ('0001015328-21-000057', '10-K', '02/26/2021', 26, 2, 2021, '0001015328', 'https://www.sec.gov/Archives/edgar/data/1015328/000101532821000057/wtfc-20201231_htm.xml', 'https://www.sec.gov/Archives/edgar/data/1015328/000101532821000057/wtfc-20201231_pre.xml', '{self.TESTDATA_PATH}wtfc-20201231_htm.xml', '{self.TESTDATA_PATH}wtfc-20201231_pre.xml');",
            f"INSERT INTO sec_report_processing ('accessionNumber', 'formType', 'filingDate', 'filingDay', 'filingMonth', 'filingYear', 'cikNumber', 'xbrlInsUrl', 'xbrlPreUrl', 'xmlNumFile', 'xmlPreFile') VALUES ('0001654954-21-002132', '10-K', '02/26/2021', 26, 2, 2021, '0001375205', 'https://www.sec.gov/Archives/edgar/data/1375205/000165495421002132/urg_10k_htm.xml', 'https://www.sec.gov/Archives/edgar/data/1375205/000165495421002132/urg-20201231_pre.xml', '{self.TESTDATA_PATH}urg_10k_htm.xml', '{self.TESTDATA_PATH}urg-20201231_pre.xml');",
            f"INSERT INTO sec_report_processing ('accessionNumber', 'formType', 'filingDate', 'filingDay', 'filingMonth', 'filingYear', 'cikNumber', 'xbrlInsUrl', 'xbrlPreUrl', 'xmlNumFile', 'xmlPreFile') VALUES ('0000073756-21-000023', '10-K', '02/26/2021', 26, 2, 2021, '0000073756', 'https://www.sec.gov/Archives/edgar/data/73756/000007375621000023/oii-20201231_htm.xml', 'https://www.sec.gov/Archives/edgar/data/73756/000007375621000023/oii-20201231_pre.xml', '{self.TESTDATA_PATH}oii-20201231_htm.xml', '{self.TESTDATA_PATH}oii-20201231_pre.xml');",
            f"INSERT INTO sec_report_processing ('accessionNumber', 'formType', 'filingDate', 'filingDay', 'filingMonth', 'filingYear', 'cikNumber', 'xbrlInsUrl', 'xbrlPreUrl', 'xmlNumFile', 'xmlPreFile') VALUES ('0001564590-21-009508', '10-K', '02/26/2021', 26, 2, 2021, '0001725057', 'https://www.sec.gov/Archives/edgar/data/1725057/000156459021009508/cday-10k_20201231_htm.xml', 'https://www.sec.gov/Archives/edgar/data/1725057/000156459021009508/cday-20201231_pre.xml', '{self.TESTDATA_PATH}cday-10k_20201231_htm.xml', '{self.TESTDATA_PATH}cday-20201231_pre.xml');",
            f"INSERT INTO sec_report_processing ('accessionNumber', 'formType', 'filingDate', 'filingDay', 'filingMonth', 'filingYear', 'cikNumber', 'xbrlInsUrl', 'xbrlPreUrl', 'xmlNumFile', 'xmlPreFile') VALUES ('0001273685-21-000032', '10-K', '02/26/2021', 26, 2, 2021, '0001273685', 'https://www.sec.gov/Archives/edgar/data/1273685/000127368521000032/nymt-20201231_htm.xml', 'https://www.sec.gov/Archives/edgar/data/1273685/000127368521000032/nymt-20201231_pre.xml', '{self.TESTDATA_PATH}nymt-20201231_htm.xml', '{self.TESTDATA_PATH}nymt-20201231_pre.xml');",
            f"INSERT INTO sec_report_processing ('accessionNumber', 'formType', 'filingDate', 'filingDay', 'filingMonth', 'filingYear', 'cikNumber', 'xbrlInsUrl', 'xbrlPreUrl', 'xmlNumFile', 'xmlPreFile') VALUES ('0001564590-21-009507', '10-K', '02/26/2021', 26, 2, 2021, '0001816816', 'https://www.sec.gov/Archives/edgar/data/1816816/000156459021009507/grsv-10k_20201231_htm.xml', 'https://www.sec.gov/Archives/edgar/data/1816816/000156459021009507/grsv-20201231_pre.xml', '{self.TESTDATA_PATH}grsv-10k_20201231_htm.xml', '{self.TESTDATA_PATH}grsv-20201231_pre.xml')",
        ]

        conn = self.get_connection()
        try:
            for sql in inserts:
                conn.execute(sql)
            conn.commit()
        finally:
            conn.close()
