from typing import List, Set, Tuple

import pandas as pd

from secdaily._00_common.DBBase import DB


class IndexProcessingDA(DB):

    def read_all_fullindex_files(self) -> pd.DataFrame:
        sql = f"""SELECT * FROM {DB.SEC_FULL_INDEX_FILE_TBL_NAME}"""
        return self._execute_read_as_df(sql)

    def insert_fullindex_file(self, year: int, qrtr: int, processdate: str):
        sql = f"""INSERT INTO {DB.SEC_FULL_INDEX_FILE_TBL_NAME} ('year', 'quarter', 'processdate')
                  VALUES({year}, {qrtr}, '{processdate}')"""
        self._execute_single(sql)

    def update_fullindex_file(self, year: int, qrtr: int, processdate: str):
        sql = f"""UPDATE {DB.SEC_FULL_INDEX_FILE_TBL_NAME} SET 'processdate' = '{processdate}'
                  WHERE  year == {year} AND quarter == {qrtr}"""
        self._execute_single(sql)

    def update_status_fullindex_file(self, year: int, qrtr: int, status: str):
        sql = f"""UPDATE {DB.SEC_FULL_INDEX_FILE_TBL_NAME} SET 'state' = '{status}'
                  WHERE  year == {year} AND quarter == {qrtr} """
        self._execute_single(sql)

    def get_adsh_by_feed_file(self, feed_file_name: str) -> Set[str]:
        sql = f"""SELECT accessionNumber FROM {DB.SEC_REPORTS_TBL_NAME} where sec_feed_file == '{feed_file_name}' """
        result: List[Tuple[str]] = self._execute_fetchall(sql)
        return {x[0] for x in result}

    def insert_feed_info(self, df: pd.DataFrame):
        conn = self.get_connection()
        try:
            df.to_sql(DB.SEC_REPORTS_TBL_NAME, conn, if_exists="append", chunksize=1000)
        finally:
            conn.close()
