from dataclasses import dataclass
from typing import List, Tuple

import pandas as pd

from secdaily._00_common.DBBase import DB


@dataclass
class UpdateDailyZip:
    accessionNumber: str
    dailyZipFile: str
    processZipDate: str


class DailyZipCreatingDA(DB):

    def read_all_copied(self) -> pd.DataFrame:
        sql = '''SELECT * FROM {} WHERE status is 'copied' '''.format(DB.SEC_REPORTS_TBL_NAME)
        return self._execute_read_as_df(sql)

    def find_ready_to_zip_adshs(self) -> pd.DataFrame:
        conn = self.get_connection()
        try:
            # select days which have entries that are not in a daily zip file
            sql = '''SELECT DISTINCT filingDate FROM {} WHERE preParseState like "parsed%" and numParseState like "parsed%" and processZipDate is NULL'''.format(
                DB.SEC_REPORT_PROCESSING_TBL_NAME)
            datesToZip_result: List[Tuple[str]] = conn.execute(sql).fetchall()
            datesToZip: List[str] = [dateToZip[0] for dateToZip in datesToZip_result]
            zipdates = ','.join("'" + zipdate + "'" for zipdate in datesToZip)

            # select all entries which belong to the found zipdates above
            sql = '''SELECT accessionNumber, filingDate, csvPreFile, csvNumfile, fiscalYearEnd FROM {} WHERE preParseState like "parsed%" and numParseState like "parsed%" and filingDate in({}) '''.format(
                DB.SEC_REPORT_PROCESSING_TBL_NAME, zipdates)
            return pd.read_sql_query(sql, conn)
        finally:
            conn.close()

    def updated_ziped_entries(self, update_list: List[UpdateDailyZip]):
        update_data = [(x.dailyZipFile, x.processZipDate, x.accessionNumber) for x in update_list]

        sql = '''UPDATE {} SET dailyZipFile = ?, processZipDate = ? WHERE accessionNumber = ?'''.format(
            DB.SEC_REPORT_PROCESSING_TBL_NAME)
        self._execute_many(sql, update_data)
