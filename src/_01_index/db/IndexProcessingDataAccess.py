from _00_common.DBBase import DB
from typing import List, Tuple, Set, Optional, Dict

import pandas as pd


class IndexProcessingDA(DB):

    def read_all_fullindex_files(self) -> pd.DataFrame:
        sql = '''SELECT * FROM {}'''.format(DB.SEC_FULL_INDEX_FILE_TBL_NAME)
        return self._execute_read_as_df(sql)

    def insert_fullindex_file(self, year: int, qrtr: int, processdate: str):
        sql = '''INSERT INTO {} ('year', 'quarter', 'processdate') VALUES({}, {}, '{}') '''.format(
            DB.SEC_FULL_INDEX_FILE_TBL_NAME, year, qrtr, processdate)
        self._execute_single(sql)

    def update_fullindex_file(self, year: int, qrtr: int, processdate: str):
        sql = '''UPDATE {} SET 'processdate' = '{}' WHERE  year == {} AND quarter == {}  '''.format(
            DB.SEC_FULL_INDEX_FILE_TBL_NAME, processdate, year, qrtr)
        self._execute_single(sql)

    def update_status_fullindex_file(self, year: int, qrtr: int, status: str):
        sql = '''UPDATE {} SET 'state' = '{}' WHERE  year == {} AND quarter == {} '''.format(
            DB.SEC_FULL_INDEX_FILE_TBL_NAME, status, year, qrtr)
        self._execute_single(sql)

    def get_adsh_by_feed_file(self, feed_file_name: str) -> Set[str]:
        sql = '''SELECT accessionNumber FROM {} where sec_feed_file == '{}' '''.format(DB.SEC_REPORTS_TBL_NAME, feed_file_name)
        result: List[Tuple[str]] = self._execute_fetchall(sql)
        return set([x[0] for x in result])

    def insert_feed_info(self, df: pd.DataFrame):
        conn = self.get_connection()
        try:
            df.to_sql(DB.SEC_REPORTS_TBL_NAME, conn, if_exists="append", chunksize=1000)
        finally:
            conn.close()