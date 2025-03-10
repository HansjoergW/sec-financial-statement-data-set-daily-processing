from typing import List, Tuple

import pandas as pd

from secdaily._00_common.DBBase import DB


class DBDebugDA(DB):

    def read_all_processing(self) -> pd.DataFrame:
        sql = '''SELECT * FROM {}'''.format(DB.SEC_REPORT_PROCESSING_TBL_NAME)
        return self._execute_read_as_df(sql)

    def get_xml_files_info_from_sec_processing_by_adshs(self, adshs: List[str]) -> List[Tuple[str, str, str]]:
        adshs = ','.join("'" + adsh + "'" for adsh in adshs)

        sql = '''SELECT accessionNumber, xmlNumFile, xmlPreFile from sec_report_processing WHERE accessionNumber in ({}) and xmlPreFile not null and xmlNumFile not null order by accessionNumber '''.format(
            adshs)
        return self._execute_fetchall(sql)

    def get_files_for_adsh(self, adsh: str) -> Tuple[str, str, str, str, str]:
        conn = self.get_connection()
        try:
            sql = '''SELECT accessionNumber, xmlPreFile, xmlNumFile, csvPreFile, csvNumFile FROM {} where accessionNumber = '{}' '''.format(
                DB.SEC_REPORT_PROCESSING_TBL_NAME, adsh)
            return conn.execute(sql).fetchone()  # !! Attention: fetchone !!
        finally:
            conn.close()

    def read_all(self) -> pd.DataFrame:
        sql = '''SELECT * FROM {}'''.format(DB.SEC_REPORTS_TBL_NAME)
        return self._execute_read_as_df(sql)

    def read_by_year_and_quarter(self, year: int, qrtr: int) -> pd.DataFrame:
        months: List = [1, 2, 3]
        offset = ((qrtr - 1) * 3)
        months = [str(x + offset) for x in months]
        month_str = ",".join(months)

        sql = '''SELECT * FROM {} WHERE filingYear = {} and filingMonth in ({})  '''.format(DB.SEC_REPORTS_TBL_NAME,
                                                                                            year,
                                                                                            month_str)
        return self._execute_read_as_df(sql)
