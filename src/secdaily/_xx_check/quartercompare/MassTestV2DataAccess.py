from dataclasses import dataclass
from typing import List, Optional

import pandas as pd

from secdaily._00_common.DBBase import DB
from secdaily._00_common.SecFileUtils import read_file_from_zip


@dataclass
class FormattedReport:
    accessionNumber: str
    numFile: str
    preFile: str


@dataclass
class UpdateMassTestV2:
    runId: int
    adsh: str
    qtr: str
    fileType: str  # either num or pre
    stmt: Optional[str] = None  # only for pre
    report: Optional[int] = None  # only for pre
    countMatching: Optional[int] = None
    countUnequal: Optional[int] = None
    countOnlyOrigin: Optional[int] = None
    countOnlyDaily: Optional[int] = None
    tagsUnequal: Optional[str] = None
    tagsOnlyOrigin: Optional[str] = None
    tagsOnlyDaily: Optional[str] = None
    quarterFile: Optional[str] = None
    dailyFile: Optional[str] = None


@dataclass
class CompareResult:
    countTotal: int
    unequalRatio: float
    missingRatioDaily: float
    missingRatioQuarter: float
    fileType: str
    stmt: Optional[str] = None


@dataclass
class ReportOverview:
    totalAdshs: int
    totalMissingInDaily: int
    totalMissingInQuarter: int
    compareResults: Optional[pd.DataFrame] = None

    def __str__(self):
        return f"""
total adshs: {self.totalAdshs}
total missing in daily: {self.totalMissingInDaily}
total total missing in quarter: {self.totalMissingInQuarter}

{self.compareResults}
"""


class MassTestV2DA(DB):

    months_in_qrtr = {1: [1, 2, 3], 2: [4, 5, 6], 3: [7, 8, 9], 4: [10, 11, 12]}

    def find_entries_for_quarter(self, year: int, qrtr: int) -> List[FormattedReport]:

        sql = f"""SELECT accessionNumber, numFormattedFile as numFile, preFormattedFile as preFile
                  FROM {DB.SEC_REPORT_PROCESSING_TBL_NAME}
                  WHERE numFormattedFile is not NULL AND preFormattedFile is not NULL
                        ANDd filingYear = {year}
                        AND filingMonth in ({','.join([str(x) for x in self.months_in_qrtr[qrtr]])})
                  """
        return self._execute_fetchall_typed(sql, FormattedReport)

    def get_total_adshs(self, run_id: int, qtr: str) -> int:
        sql = f"""
        SELECT COUNT(DISTINCT adsh) as totalAdshs
        FROM {DB.MASS_TESTING_V2_TBL_NAME}
        WHERE runId = {run_id} AND qtr = '{qtr}'"""

        result = self._execute_fetchall(sql)
        return result[0][0]

    def get_total_missing_daily(self, run_id: int, qtr: str) -> int:
        sql = f"""
            SELECT count(DISTINCT adsh) as totalMissingQuarter
            FROM {DB.MASS_TESTING_V2_TBL_NAME}
            WHERE runId={run_id} AND qtr='{qtr}' AND fileType="pre" AND dailyFile IS NULL;
        """
        result = self._execute_fetchall(sql)
        return result[0][0]

    def get_total_missing_quarter(self, run_id: int, qtr: str) -> int:
        sql = f"""
            SELECT count(DISTINCT adsh) as totalMissingDaily
            FROM {DB.MASS_TESTING_V2_TBL_NAME}
            WHERE runId={run_id} AND qtr='{qtr}' AND fileType="pre" AND quarterFile IS NULL;
        """
        result = self._execute_fetchall(sql)
        return result[0][0]

    def get_pre_overview(self, run_id: int, qtr: str) -> pd.DataFrame:
        sql = f"""
                    WITH base_counts AS (
                        SELECT
                            fileType,
                            stmt,
                            SUM(countMatching + countOnlyOrigin + countOnlyDaily) as countTotal,
                            SUM(countUnequal) as totalUnequal,
                            SUM(countOnlyOrigin) as totalOnlyOrigin,
                            SUM(countOnlyDaily) as totalOnlyDaily
                        FROM {DB.MASS_TESTING_V2_TBL_NAME}
                        WHERE fileType = 'pre'
                        AND stmt IS NOT NULL
                        AND runId = {run_id}
                        AND qtr = '{qtr}'
                        GROUP BY stmt
                    )
                    SELECT
                        fileType,
                        stmt,
                        countTotal,
                        CAST(totalUnequal AS FLOAT) / countTotal as unequalRatio,
                        CAST(totalOnlyOrigin AS FLOAT) / countTotal as missingRatioDaily,
                        CAST(totalOnlyDaily AS FLOAT) / countTotal as missingRatioQuarter
                    FROM base_counts
                    ORDER BY stmt;
                            """
        return self._execute_read_as_df(sql)

    def get_num_overview(self, run_id: int, qtr: str) -> pd.DataFrame:
        sql = f"""
                WITH base_counts AS (
                    SELECT
                        fileType,
                        stmt,
                        SUM(countMatching + countOnlyOrigin + countOnlyDaily) as countTotal,
                        SUM(countMatching) as totalMatching,
                        SUM(countUnequal) as totalUnequal,
                        SUM(countOnlyOrigin) as totalOnlyOrigin,
                        SUM(countOnlyDaily) as totalOnlyDaily
                    FROM {DB.MASS_TESTING_V2_TBL_NAME}
                    WHERE fileType = 'num'
                    AND countMatching IS NOT NULL
                    AND runId = {run_id}
                    AND qtr = '{qtr}'
                )
                SELECT
                    fileType,
                    stmt,
                    countTotal,
                    CAST(totalUnequal AS FLOAT) / countTotal as unequalRatio,
                    CAST(totalOnlyOrigin AS FLOAT) / countTotal as missingRatioDaily,
                    CAST(totalOnlyDaily AS FLOAT) / countTotal as missingRatioQuarter
                FROM base_counts;
            """

        return self._execute_read_as_df(sql)

    def get_report_overview(self, run_id: int, qtr: str) -> ReportOverview:
        totalAdshs = self.get_total_adshs(run_id, qtr)
        totalMissingInDaily = self.get_total_missing_daily(run_id, qtr)
        totalMissingInQuarter = self.get_total_missing_quarter(run_id, qtr)

        pre_results = self.get_pre_overview(run_id, qtr)
        num_results = self.get_num_overview(run_id, qtr)

        compare_results = pd.concat([pre_results, num_results])

        compare_results = compare_results.round({"unequalRatio": 3, "missingRatioDaily": 3, "missingRatioQuarter": 3})

        report_overview = ReportOverview(
            totalAdshs=totalAdshs,
            totalMissingInDaily=totalMissingInDaily,
            totalMissingInQuarter=totalMissingInQuarter,
            compareResults=compare_results,
        )

        return report_overview

    def insert_test_result(self, update_list: List[UpdateMassTestV2]):
        sql = f"""INSERT INTO {DB.MASS_TESTING_V2_TBL_NAME}
                    (runId, adsh, qtr, fileType, stmt, report,
                     countMatching, countUnequal, countOnlyOrigin, countOnlyDaily,
                     tagsUnequal, tagsOnlyOrigin, tagsOnlyDaily, quarterFile, dailyFile)
                     VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

        # Konvertiere UpdateMassTestV2 Objekte in Tupel
        params = [
            (
                update.runId,
                update.adsh,
                update.qtr,
                update.fileType,
                update.stmt,
                update.report,
                update.countMatching,
                update.countUnequal,
                update.countOnlyOrigin,
                update.countOnlyDaily,
                update.tagsUnequal,
                update.tagsOnlyOrigin,
                update.tagsOnlyDaily,
                update.quarterFile,
                update.dailyFile,
            )
            for update in update_list
        ]

        self._execute_many(sql, params)


class QuarterFileAccess:

    def __init__(self, quarter_file: str):
        self.quarter_file = quarter_file
        self.num_df: Optional[pd.DataFrame] = None
        self.pre_df: Optional[pd.DataFrame] = None
        self.sub_df: Optional[pd.DataFrame] = None

    def load_data(self):
        self.num_df = read_file_from_zip(self.quarter_file, "num.txt")
        self.pre_df = read_file_from_zip(self.quarter_file, "pre.txt")
        self.sub_df = read_file_from_zip(self.quarter_file, "sub.txt")


if __name__ == "__main__":
    workdir = "d:/secprocessing2/"
    dbmgr = MassTestV2DA(workdir)

    entries: List[FormattedReport] = dbmgr.find_entries_for_quarter(year=2024, qrtr=4)
    print(len(entries))
