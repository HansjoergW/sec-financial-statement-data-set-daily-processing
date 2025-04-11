from dataclasses import dataclass
from typing import List, Tuple

import pandas as pd

from secdaily._00_common.BaseDefinitions import QRTR_TO_MONTHS
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


# @dataclass
# class DailyZipProcessEntry:
#     accessionNumber: str
#     filingMonth: int
#     filingYear: int
#     numFormattedFile: str
#     preFormattedFile: str
#     fiscalYearEnd: str


class DailyZipCreatingDA(DB):

    def find_incomplete_months(self) -> List[IncompleteMonth]:
        sql = f"""SELECT DISTINCT filingMonth, filingYear
                 FROM {DB.SEC_REPORT_PROCESSING_TBL_NAME}
                 WHERE dailyZipFile is NULL and processZipDate is NULL AND formatState="formatted";
                """
        return self._execute_fetchall_typed(sql, IncompleteMonth)

    def find_entries_for_quarter(self, year: int, qrtr: int) -> pd.DataFrame:
        months_in_qrtr = QRTR_TO_MONTHS[qrtr]
        months_str = ",".join([str(x) for x in months_in_qrtr])

        sql = f"""SELECT accessionNumber, filingMonth, filingYear,numFormattedFile, preFormattedFile, fiscalYearEnd
                  FROM {DB.SEC_REPORT_PROCESSING_TBL_NAME}
                  WHERE numFormattedFile is not NULL and preFormattedFile is not NULL
                      and filingYear = {year} and filingMonth in ({months_str})
                  """
        return self._execute_read_as_df(sql)

    def read_all_copied(self) -> pd.DataFrame:
        sql = """SELECT * FROM {} WHERE status is 'copied' """.format(DB.SEC_REPORTS_TBL_NAME)
        return self._execute_read_as_df(sql)

    def find_ready_to_zip_adshs(self) -> pd.DataFrame:
        conn = self.get_connection()
        try:
            # select days which have entries that are not in a daily zip file
            sql = """SELECT DISTINCT filingDate FROM {} WHERE preParseState like "parsed%" and numParseState like "parsed%" and processZipDate is NULL""".format(
                DB.SEC_REPORT_PROCESSING_TBL_NAME
            )
            datesToZip_result: List[Tuple[str]] = conn.execute(sql).fetchall()
            datesToZip: List[str] = [dateToZip[0] for dateToZip in datesToZip_result]
            zipdates = ",".join("'" + zipdate + "'" for zipdate in datesToZip)

            # select all entries which belong to the found zipdates above
            sql = """SELECT accessionNumber, filingDate, csvPreFile, csvNumfile, fiscalYearEnd FROM {} WHERE preParseState like "parsed%" and numParseState like "parsed%" and filingDate in({}) """.format(
                DB.SEC_REPORT_PROCESSING_TBL_NAME, zipdates
            )
            return pd.read_sql_query(sql, conn)
        finally:
            conn.close()

    def updated_ziped_entries(self, update_list: List[UpdateDailyZip]):
        update_data = [(x.dailyZipFile, x.processZipDate, x.accessionNumber) for x in update_list]

        sql = """UPDATE {} SET dailyZipFile = ?, processZipDate = ? WHERE accessionNumber = ?""".format(
            DB.SEC_REPORT_PROCESSING_TBL_NAME
        )
        self._execute_many(sql, update_data)
