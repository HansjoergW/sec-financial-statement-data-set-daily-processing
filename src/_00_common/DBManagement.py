import os
import sqlite3
from typing import List, Tuple, Set
import pandas as pd
import glob

scriptpath = os.path.realpath(__file__ + "/..")
testdata_path = scriptpath + '/testdata/'

SEC_FEED_TBL_NAME = "sec_feeds"
SEC_INDEX_FILE_TBL_NAME = "sec_index_file"
SEC_REPORT_PROCESSING_TBL_NAME = "sec_report_processing"

SEC_FEED_TBL_COLS = (
    'companyName', 'formType', 'filingDate', 'cikNumber',
    'accessionNumber', 'fileNumber', 'acceptanceDatetime',
    'period', 'assistantDirector', 'assignedSic', 'fiscalYearEnd',
    'xbrlInsUrl', 'xbrlCalUrl', 'xbrlDefUrl', 'xbrlLabUrl', 'xbrlPreUrl',
    'sec_feed_file'
)


class DBManager():

    def __init__(self, work_dir="edgar/"):
        self.work_dir = work_dir
        self.database = os.path.join(self.work_dir, 'sec_processing.db')

    def get_connection(self):
        return sqlite3.connect(self.database)

    def _create_db(self):
        """

        """
        ddl_folder = os.path.realpath(__file__ + "/../../../ddl")
        sqlfiles = list(glob.glob(ddl_folder + "/*.sql"))
        sorted(sqlfiles)

        if not os.path.isdir(self.work_dir):
            os.makedirs(self.work_dir)

        conn = self.get_connection()
        curr = conn.cursor()
        for sqlfile in sqlfiles:
            script = open(sqlfile, 'r').read()
            curr.executescript(script)
            conn.commit()
        conn.close()

    # ---- index files / sec-feed-file table
    def read_all_index_files(self) -> pd.DataFrame:
        conn = self.get_connection()
        try:
            sql = '''SELECT * FROM {}'''.format(SEC_INDEX_FILE_TBL_NAME)
            return pd.read_sql_query(sql, conn)
        finally:
            conn.close()

    def insert_index_file(self, name:str, processdate:str):
        conn = self.get_connection()
        try:
            sql = '''INSERT INTO {} ('sec_feed_file', 'processdate') VALUES('{}','{}') '''.format(SEC_INDEX_FILE_TBL_NAME, name, processdate)
            conn.execute(sql)
            conn.commit()
        finally:
            conn.close()

    def update_index_file(self, name:str, processdate:str):
        conn = self.get_connection()
        try:
            sql = '''UPDATE {} SET 'processdate' = '{}' WHERE  sec_feed_file == '{}' '''.format(SEC_INDEX_FILE_TBL_NAME, processdate, name)
            conn.execute(sql)
            conn.commit()
        finally:
            conn.close()

    def update_status_index_file(self, name:str, status:str):
        conn = self.get_connection()
        try:
            sql = '''UPDATE {} SET 'status' = '{}' WHERE  sec_feed_file == '{}' '''.format(SEC_INDEX_FILE_TBL_NAME, status, name)
            conn.execute(sql)
            conn.commit()
        finally:
            conn.close()

    # - processing file / sec-report-processing table
    def read_all_processing(self) -> pd.DataFrame:
        conn = self.get_connection()
        try:
            sql = '''SELECT * FROM {}'''.format(SEC_REPORT_PROCESSING_TBL_NAME)
            return pd.read_sql_query(sql, conn)
        finally:
            conn.close()

    def get_xml_files_info_from_sec_processing_by_adshs(self, adshs: List[str]) -> List[Tuple[str, str, str]]:
        conn = self.get_connection()
        adshs = ','.join("'" + adsh + "'" for adsh in adshs)
        try:
            sql = '''SELECT accessionNumber, xmlNumFile, xmlPreFile from sec_report_processing WHERE accessionNumber in ({}) and xmlPreFile not null and xmlNumFile not null order by accessionNumber '''.format(adshs)
            return conn.execute(sql).fetchall()
        finally:
            conn.close()

    def get_files_for_adsh(self, adsh: str) -> Tuple[str, str, str, str, str]:
        conn = self.get_connection()
        try:
            sql = '''SELECT accessionNumber, xmlPreFile, xmlNumFile, csvPreFile, csvNumFile FROM {} where accessionNumber = '{}' '''.format(SEC_REPORT_PROCESSING_TBL_NAME, adsh)
            return conn.execute(sql).fetchone()
        finally:
            conn.close()


    def find_missing_xmlNumFiles(self) -> List[Tuple[str, str]]:
        conn = self.get_connection()
        try:
            sql = '''SELECT accessionNumber, xbrlInsUrl, insSize FROM {} WHERE xmlNumFile is NULL'''.format(SEC_REPORT_PROCESSING_TBL_NAME)

            return conn.execute(sql).fetchall()
        finally:
            conn.close()

    def find_missing_xmlPreFiles(self) -> List[Tuple[str, str]]:
        conn = self.get_connection()
        try:
            sql = '''SELECT accessionNumber, xbrlPreUrl, preSize FROM {} WHERE xmlPreFile is NULL'''.format(SEC_REPORT_PROCESSING_TBL_NAME)

            return conn.execute(sql).fetchall()
        finally:
            conn.close()

    def update_processing_xml_num_file(self, update_data: List[Tuple[str]]):
        conn = self.get_connection()
        try:
            sql = '''UPDATE {} SET xmlNumFile = ? WHERE accessionNumber = ?'''.format(SEC_REPORT_PROCESSING_TBL_NAME)
            conn.executemany(sql, update_data)
            conn.commit()
        finally:
            conn.close()

    def update_processing_xml_pre_file(self, update_data: List[Tuple[str]]):
        conn = self.get_connection()
        try:
            sql = '''UPDATE {} SET xmlPreFile = ? WHERE accessionNumber = ?'''.format(SEC_REPORT_PROCESSING_TBL_NAME)
            conn.executemany(sql, update_data)
            conn.commit()
        finally:
            conn.close()

    def find_unparsed_numFiles(self) -> List[Tuple[str, str]]:
        conn = self.get_connection()
        try:
            sql = '''SELECT accessionNumber, xmlNumFile FROM {} WHERE csvNumFile is NULL and numParseState is not "parsed"'''.format(SEC_REPORT_PROCESSING_TBL_NAME)

            return conn.execute(sql).fetchall()
        finally:
            conn.close()

    def find_unparsed_preFiles(self) -> List[Tuple[str, str]]:
        conn = self.get_connection()
        try:
            sql = '''SELECT accessionNumber, xmlPreFile FROM {} WHERE csvPreFile is NULL and preParseState is not "parsed"'''.format(SEC_REPORT_PROCESSING_TBL_NAME)

            return conn.execute(sql).fetchall()
        finally:
            conn.close()

    def update_parsed_num_file(self, update_data: List[Tuple[str]]):
        conn = self.get_connection()
        try:
            sql = '''UPDATE {} SET csvNumFile = ?, numParseDate = ?, numParseState = ? WHERE accessionNumber = ?'''.format(SEC_REPORT_PROCESSING_TBL_NAME)
            conn.executemany(sql, update_data)
            conn.commit()
        finally:
            conn.close()

    def update_parsed_pre_file(self, update_data: List[Tuple[str]]):
        conn = self.get_connection()
        try:
            sql = '''UPDATE {} SET csvPreFile = ?, preParseDate = ?, preParseState = ? WHERE accessionNumber = ?'''.format(SEC_REPORT_PROCESSING_TBL_NAME)
            conn.executemany(sql, update_data)
            conn.commit()
        finally:
            conn.close()

    # - report metadata / sec-feed table
    def read_all(self) -> pd.DataFrame:
        conn = self.get_connection()
        try:
            sql = '''SELECT * FROM {}'''.format(SEC_FEED_TBL_NAME)
            return pd.read_sql_query(sql, conn)
        finally:
            conn.close()

    def insert_feed_info(self, df: pd.DataFrame):
        conn = self.get_connection()
        try:
            df.to_sql(SEC_FEED_TBL_NAME, conn, if_exists="append", chunksize=1000)
        finally:
            conn.close()

    def find_missing_xbrl_ins_urls(self) -> List[Tuple[str]]:
        conn = self.get_connection()
        try:
            sql = '''SELECT accessionNumber, xbrlInsUrl, xbrlPreUrl FROM {} WHERE xbrlInsUrl is NULL'''.format(
                SEC_FEED_TBL_NAME)

            return conn.execute(sql).fetchall()
        finally:
            conn.close()

    # TODO: korrekterweise muesste man hier die WHERE neu zusätzlich mit sec_feed_file ergänzen
    def update_xbrl_ins_urls(self, update_data: List[Tuple[str, str, str]]):
        conn = self.get_connection()
        try:
            sql = '''UPDATE {} SET xbrlInsUrl = ?, insSize = ? WHERE accessionNumber = ?'''.format(SEC_FEED_TBL_NAME)
            conn.executemany(sql, update_data)
            conn.commit()
        finally:
            conn.close()

    def get_adsh_by_feed_file(self, feed_file_name:str) -> Set[str]:
        conn = self.get_connection()
        try:
            sql = '''SELECT accessionNumber FROM sec_feeds where sec_feed_file == '{}' '''.format(feed_file_name)
            result: List[Tuple[str]] = conn.execute(sql).fetchall()
            return set([x[0] for x in result])
        finally:
            conn.close()

    def find_duplicated_adsh(self) -> List[str]:
        conn = self.get_connection()
        try:
            sql = '''SELECT COUNT(*) as mycount, accessionNumber FROM sec_feeds WHERE status is null GROUP BY accessionNumber'''
            duplicated_df = pd.read_sql_query(sql, conn)

            duplicated_df = duplicated_df[duplicated_df.mycount > 1].copy()
            return duplicated_df.accessionNumber.tolist()

        finally:
            conn.close()

    def mark_duplicated_adsh(self, adsh: str):
        conn = self.get_connection()
        try:
            sql = '''SELECT accessionNumber, sec_feed_file FROM sec_feeds WHERE accessionNumber= '{}' and status is null order by sec_feed_file'''.format(adsh)
            result: List[Tuple[str]] = conn.execute(sql).fetchall()

            update_sql =  '''UPDATE {} SET status = 'duplicated' WHERE accessionNumber = ? and sec_feed_file = ? '''.format(SEC_FEED_TBL_NAME)
            conn.executemany(update_sql, result[1:])
            conn.commit()
        finally:
            conn.close()

    # copies entries from the feed table to the processing table if they are not already present
    def copy_uncopied_entries(self) -> int:
        conn = self.get_connection()
        try:
            sql = '''SELECT accessionNumber, cikNumber, filingDate, formType, xbrlInsUrl, insSize, xbrlPreUrl, preSize  FROM sec_feeds WHERE status is null and xbrlInsUrl is not null'''
            to_copy_df =  pd.read_sql_query(sql, conn)

            to_copy_df['filingMonth'] = pd.to_numeric(to_copy_df.filingDate.str.slice(0,2), downcast="integer")
            to_copy_df['filingDay'] = pd.to_numeric(to_copy_df.filingDate.str.slice(3,5), downcast="integer")
            to_copy_df['filingYear'] = pd.to_numeric(to_copy_df.filingDate.str.slice(6,10), downcast="integer")

            to_copy_df.to_sql(SEC_REPORT_PROCESSING_TBL_NAME, conn, index=False, if_exists="append", chunksize=1000)

            update_sql =  '''UPDATE {} SET status = 'copied' WHERE accessionNumber = ? and status is null '''.format(SEC_FEED_TBL_NAME)
            adshs = to_copy_df.accessionNumber.values.tolist()
            tupleslist = [tuple(x.split()) for x in adshs]

            conn.executemany(update_sql, tupleslist)

            conn.commit()
            return len(to_copy_df)
        finally:
            conn.close()

    def create_test_data(self):
        inserts = [
            "INSERT INTO sec_feeds ('accessionNumber', 'companyName', 'formType', 'filingDate', 'cikNumber', 'fileNumber', 'acceptanceDatetime', 'period', 'assistantDirector', 'assignedSic', 'fiscalYearEnd', 'xbrlInsUrl', 'xbrlCalUrl', 'xbrlDefUrl', 'xbrlLabUrl', 'xbrlPreUrl','sec_feed_file') VALUES ('0001437749-21-004277', 'COHU INC', '10-K', '02/26/2021', '0000021535', '001-04298', '20210226173215', '20201226', 'Office of Life Sciences', '3825', '1226', 'https://www.sec.gov/Archives/edgar/data/21535/000143774921004277/cohu20201226_10k_htm.xml','https://www.sec.gov/Archives/edgar/data/21535/000143774921004277/cohu-20201226_cal.xml', 'https://www.sec.gov/Archives/edgar/data/21535/000143774921004277/cohu-20201226_def.xml', 'https://www.sec.gov/Archives/edgar/data/21535/000143774921004277/cohu-20201226_lab.xml', 'https://www.sec.gov/Archives/edgar/data/21535/000143774921004277/cohu-20201226_pre.xml','file1.xml');",
            "INSERT INTO sec_feeds ('accessionNumber', 'companyName', 'formType', 'filingDate', 'cikNumber', 'fileNumber', 'acceptanceDatetime', 'period', 'assistantDirector', 'assignedSic', 'fiscalYearEnd', 'xbrlInsUrl', 'xbrlCalUrl', 'xbrlDefUrl', 'xbrlLabUrl', 'xbrlPreUrl','sec_feed_file') VALUES ('0001015328-21-000057', 'WINTRUST FINANCIAL CORP', '10-K', '02/26/2021', '0001015328', '001-35077', '20210226172958', '20201231', 'Office of Finance', '6022', '1231', 'https://www.sec.gov/Archives/edgar/data/1015328/000101532821000057/wtfc-20201231_htm.xml', 'https://www.sec.gov/Archives/edgar/data/1015328/000101532821000057/wtfc-20201231_cal.xml', 'https://www.sec.gov/Archives/edgar/data/1015328/000101532821000057/wtfc-20201231_def.xml', 'https://www.sec.gov/Archives/edgar/data/1015328/000101532821000057/wtfc-20201231_lab.xml', 'https://www.sec.gov/Archives/edgar/data/1015328/000101532821000057/wtfc-20201231_pre.xml','file1.xml');",
            "INSERT INTO sec_feeds ('accessionNumber', 'companyName', 'formType', 'filingDate', 'cikNumber', 'fileNumber', 'acceptanceDatetime', 'period', 'assistantDirector', 'assignedSic', 'fiscalYearEnd', 'xbrlInsUrl', 'xbrlCalUrl', 'xbrlDefUrl', 'xbrlLabUrl', 'xbrlPreUrl','sec_feed_file') VALUES ('0001654954-21-002132', 'UR-ENERGY INC', '10-K', '02/26/2021', '0001375205', '001-33905', '20210226172939', '20201231', 'Office of Energy & Transportation', '1040', '1231', 'https://www.sec.gov/Archives/edgar/data/1375205/000165495421002132/urg_10k_htm.xml', 'https://www.sec.gov/Archives/edgar/data/1375205/000165495421002132/urg-20201231_cal.xml', 'https://www.sec.gov/Archives/edgar/data/1375205/000165495421002132/urg-20201231_def.xml', 'https://www.sec.gov/Archives/edgar/data/1375205/000165495421002132/urg-20201231_lab.xml', 'https://www.sec.gov/Archives/edgar/data/1375205/000165495421002132/urg-20201231_pre.xml','file1.xml');",
            "INSERT INTO sec_feeds ('accessionNumber', 'companyName', 'formType', 'filingDate', 'cikNumber', 'fileNumber', 'acceptanceDatetime', 'period', 'assistantDirector', 'assignedSic', 'fiscalYearEnd', 'xbrlInsUrl', 'xbrlCalUrl', 'xbrlDefUrl', 'xbrlLabUrl', 'xbrlPreUrl','sec_feed_file') VALUES ('0000073756-21-000023', 'OCEANEERING INTERNATIONAL INC', '10-K', '02/26/2021', '0000073756', '001-10945', '20210226172622', '20201231', 'Office of Energy & Transportation', '1389', '1231', 'https://www.sec.gov/Archives/edgar/data/73756/000007375621000023/oii-20201231_htm.xml', 'https://www.sec.gov/Archives/edgar/data/73756/000007375621000023/oii-20201231_cal.xml', 'https://www.sec.gov/Archives/edgar/data/73756/000007375621000023/oii-20201231_def.xml', 'https://www.sec.gov/Archives/edgar/data/73756/000007375621000023/oii-20201231_lab.xml', 'https://www.sec.gov/Archives/edgar/data/73756/000007375621000023/oii-20201231_pre.xml','file1.xml');",
            "INSERT INTO sec_feeds ('accessionNumber', 'companyName', 'formType', 'filingDate', 'cikNumber', 'fileNumber', 'acceptanceDatetime', 'period', 'assistantDirector', 'assignedSic', 'fiscalYearEnd', 'xbrlInsUrl', 'xbrlCalUrl', 'xbrlDefUrl', 'xbrlLabUrl', 'xbrlPreUrl','sec_feed_file') VALUES ('0001564590-21-009508', 'Ceridian HCM Holding Inc.', '10-K', '02/26/2021', '0001725057', '001-38467', '20210226172344', '20201231', 'Office of Technology', '7372', '1231', 'https://www.sec.gov/Archives/edgar/data/1725057/000156459021009508/cday-10k_20201231_htm.xml','https://www.sec.gov/Archives/edgar/data/1725057/000156459021009508/cday-20201231_cal.xml', 'https://www.sec.gov/Archives/edgar/data/1725057/000156459021009508/cday-20201231_def.xml', 'https://www.sec.gov/Archives/edgar/data/1725057/000156459021009508/cday-20201231_lab.xml', 'https://www.sec.gov/Archives/edgar/data/1725057/000156459021009508/cday-20201231_pre.xml','file1.xml');",
            "INSERT INTO sec_feeds ('accessionNumber', 'companyName', 'formType', 'filingDate', 'cikNumber', 'fileNumber', 'acceptanceDatetime', 'period', 'assistantDirector', 'assignedSic', 'fiscalYearEnd', 'xbrlInsUrl', 'xbrlCalUrl', 'xbrlDefUrl', 'xbrlLabUrl', 'xbrlPreUrl','sec_feed_file') VALUES ('0001273685-21-000032', 'NEW YORK MORTGAGE TRUST INC', '10-K', '02/26/2021', '0001273685', '001-32216', '20210226172340', '20201231', 'Office of Real Estate & Construction', '6798', '1231', 'https://www.sec.gov/Archives/edgar/data/1273685/000127368521000032/nymt-20201231_htm.xml', 'https://www.sec.gov/Archives/edgar/data/1273685/000127368521000032/nymt-20201231_cal.xml', 'https://www.sec.gov/Archives/edgar/data/1273685/000127368521000032/nymt-20201231_def.xml', 'https://www.sec.gov/Archives/edgar/data/1273685/000127368521000032/nymt-20201231_lab.xml', 'https://www.sec.gov/Archives/edgar/data/1273685/000127368521000032/nymt-20201231_pre.xml','file1.xml');",
            "INSERT INTO sec_feeds ('accessionNumber', 'companyName', 'formType', 'filingDate', 'cikNumber', 'fileNumber', 'acceptanceDatetime', 'period', 'assistantDirector', 'assignedSic', 'fiscalYearEnd', 'xbrlInsUrl', 'xbrlCalUrl', 'xbrlDefUrl', 'xbrlLabUrl', 'xbrlPreUrl','sec_feed_file') VALUES ('0001564590-21-009507', 'Gores Holdings V Inc.', '10-K', '02/26/2021', '0001816816', '001-39429', '20210226172257', '20201231', 'Office of Real Estate & Construction', '6770', '1231', 'https://www.sec.gov/Archives/edgar/data/1816816/000156459021009507/grsv-10k_20201231_htm.xml', 'https://www.sec.gov/Archives/edgar/data/1816816/000156459021009507/grsv-20201231_cal.xml', 'https://www.sec.gov/Archives/edgar/data/1816816/000156459021009507/grsv-20201231_def.xml', 'https://www.sec.gov/Archives/edgar/data/1816816/000156459021009507/grsv-20201231_lab.xml', 'https://www.sec.gov/Archives/edgar/data/1816816/000156459021009507/grsv-20201231_pre.xml','file1.xml');"
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
            "INSERT INTO sec_report_processing ('accessionNumber', 'formType', 'filingDate', 'cikNumber', 'xbrlInsUrl', 'xbrlPreUrl', 'xmlNumFile', 'xmlPreFile') VALUES ('0001437749-21-004277', '10-K', '02/26/2021', '0000021535', 'https://www.sec.gov/Archives/edgar/data/21535/000143774921004277/cohu20201226_10k_htm.xml', 'https://www.sec.gov/Archives/edgar/data/21535/000143774921004277/cohu-20201226_pre.xml', '{0}cohu20201226_10k_htm.xml', '{0}cohu-20201226_pre.xml');".format(testdata_path),
            "INSERT INTO sec_report_processing ('accessionNumber', 'formType', 'filingDate', 'cikNumber', 'xbrlInsUrl', 'xbrlPreUrl', 'xmlNumFile', 'xmlPreFile') VALUES ('0001015328-21-000057', '10-K', '02/26/2021', '0001015328', 'https://www.sec.gov/Archives/edgar/data/1015328/000101532821000057/wtfc-20201231_htm.xml', 'https://www.sec.gov/Archives/edgar/data/1015328/000101532821000057/wtfc-20201231_pre.xml', '{0}wtfc-20201231_htm.xml', '{0}wtfc-20201231_pre.xml');".format(testdata_path),
            "INSERT INTO sec_report_processing ('accessionNumber', 'formType', 'filingDate', 'cikNumber', 'xbrlInsUrl', 'xbrlPreUrl', 'xmlNumFile', 'xmlPreFile') VALUES ('0001654954-21-002132', '10-K', '02/26/2021', '0001375205', 'https://www.sec.gov/Archives/edgar/data/1375205/000165495421002132/urg_10k_htm.xml', 'https://www.sec.gov/Archives/edgar/data/1375205/000165495421002132/urg-20201231_pre.xml', '{0}urg_10k_htm.xml', '{0}urg-20201231_pre.xml');".format(testdata_path),
            "INSERT INTO sec_report_processing ('accessionNumber', 'formType', 'filingDate', 'cikNumber', 'xbrlInsUrl', 'xbrlPreUrl', 'xmlNumFile', 'xmlPreFile') VALUES ('0000073756-21-000023', '10-K', '02/26/2021', '0000073756', 'https://www.sec.gov/Archives/edgar/data/73756/000007375621000023/oii-20201231_htm.xml', 'https://www.sec.gov/Archives/edgar/data/73756/000007375621000023/oii-20201231_pre.xml', '{0}oii-20201231_htm.xml', '{0}oii-20201231_pre.xml');".format(testdata_path),
            "INSERT INTO sec_report_processing ('accessionNumber', 'formType', 'filingDate', 'cikNumber', 'xbrlInsUrl', 'xbrlPreUrl', 'xmlNumFile', 'xmlPreFile') VALUES ('0001564590-21-009508', '10-K', '02/26/2021', '0001725057', 'https://www.sec.gov/Archives/edgar/data/1725057/000156459021009508/cday-10k_20201231_htm.xml', 'https://www.sec.gov/Archives/edgar/data/1725057/000156459021009508/cday-20201231_pre.xml', '{0}cday-10k_20201231_htm.xml', '{0}cday-20201231_pre.xml');".format(testdata_path),
            "INSERT INTO sec_report_processing ('accessionNumber', 'formType', 'filingDate', 'cikNumber', 'xbrlInsUrl', 'xbrlPreUrl', 'xmlNumFile', 'xmlPreFile') VALUES ('0001273685-21-000032', '10-K', '02/26/2021', '0001273685', 'https://www.sec.gov/Archives/edgar/data/1273685/000127368521000032/nymt-20201231_htm.xml', 'https://www.sec.gov/Archives/edgar/data/1273685/000127368521000032/nymt-20201231_pre.xml', '{0}nymt-20201231_htm.xml', '{0}nymt-20201231_pre.xml');".format(testdata_path),
            "INSERT INTO sec_report_processing ('accessionNumber', 'formType', 'filingDate', 'cikNumber', 'xbrlInsUrl', 'xbrlPreUrl', 'xmlNumFile', 'xmlPreFile') VALUES ('0001564590-21-009507', '10-K', '02/26/2021', '0001816816', 'https://www.sec.gov/Archives/edgar/data/1816816/000156459021009507/grsv-10k_20201231_htm.xml', 'https://www.sec.gov/Archives/edgar/data/1816816/000156459021009507/grsv-20201231_pre.xml', '{0}grsv-10k_20201231_htm.xml', '{0}grsv-20201231_pre.xml')".format(testdata_path)
        ]

        conn = self.get_connection()
        try:
            for sql in inserts:
                conn.execute(sql)
            conn.commit()
        finally:
            conn.close()
