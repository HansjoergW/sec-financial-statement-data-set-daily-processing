from dataclasses import dataclass
from typing import List, Tuple

import pandas as pd

from secdaily._00_common.DBBase import DB


@dataclass
class UpdateDailyZip:
    accessionNumber: str
    dailyZipFile: str
    processZipDate: str


@dataclass
class IncompleteMonth:
    filingMonth: int
    filingYear: int


class DailyZipCreatingDA(DB):

    def read_all_copied(self) -> pd.DataFrame:
        sql = f"""SELECT * FROM {DB.SEC_REPORTS_TBL_NAME} WHERE status is 'copied' """
        return self._execute_read_as_df(sql)

    def find_ready_to_zip_adshs(self) -> pd.DataFrame:
        conn = self.get_connection()
        try:
            # select days which have entries that are not in a daily zip file
            sql = f"""SELECT DISTINCT filingDate
                      FROM {DB.SEC_REPORT_PROCESSING_TBL_NAME}
                      WHERE preParseState like "parsed%" AND numParseState like "parsed%"
                            AND preFormattedFile is not null AND numFormattedFile is not null
                            AND processZipDate is NULL
                    """
            datesToZip_result: List[Tuple[str]] = conn.execute(sql).fetchall()
            datesToZip: List[str] = [dateToZip[0] for dateToZip in datesToZip_result]
            zipdates = ",".join("'" + zipdate + "'" for zipdate in datesToZip)

            # select all entries which belong to the found zipdates above
            sql = f"""SELECT accessionNumber, filingDate, preFormattedFile, numFormattedFile, fiscalYearEnd
                     FROM {DB.SEC_REPORT_PROCESSING_TBL_NAME}
                     WHERE preParseState like "parsed%" and numParseState like "parsed%" and filingDate in({zipdates})
                     """

            return pd.read_sql_query(sql, conn)
        finally:
            conn.close()

    def updated_ziped_entries(self, update_list: List[UpdateDailyZip]):
        update_data = [(x.dailyZipFile, x.processZipDate, x.accessionNumber) for x in update_list]

        sql = f"""UPDATE {DB.SEC_REPORT_PROCESSING_TBL_NAME}
                  SET dailyZipFile = ?, processZipDate = ? WHERE accessionNumber = ?"""
        self._execute_many(sql, update_data)
