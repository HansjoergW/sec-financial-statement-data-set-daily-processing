"""
Data access module for the housekeeping functionality. Provides database operations for finding and deleting
reports before a specified quarter.
"""

import logging
from dataclasses import dataclass
from typing import List

from secdaily._00_common.BaseDefinitions import QuarterInfo
from secdaily._00_common.DBBase import DB


@dataclass
class ReportToCleanup:
    """Class representing a report that should be cleaned up."""

    accessionNumber: str
    filingYear: int
    filingMonth: int
    filingDay: int
    xmlNumFile: str | None = None
    xmlPreFile: str | None = None
    xmlLabFile: str | None = None
    csvNumFile: str | None = None
    csvPreFile: str | None = None
    csvLabFile: str | None = None
    numFormattedFile: str | None = None
    preFormattedFile: str | None = None
    dailyZipFile: str | None = None


class HousekeepingDataAccess(DB):
    """Data access class for housekeeping operations."""

    def find_reports_before_quarter(self, start_qrtr_info: QuarterInfo) -> List[ReportToCleanup]:
        """
        Find all reports with filing date before the specified quarter.

        Args:
            start_qrtr_info: The starting quarter (reports before this will be returned)

        Returns:
            List of ReportToCleanup objects
        """
        # Calculate the quarter value for comparison
        start_qrtr_value = start_qrtr_info.qrtr_value

        # Find reports with filing date before the specified quarter
        sql = f"""
            SELECT accessionNumber, filingYear, filingMonth, filingDay,
                   xmlNumFile, xmlPreFile, xmlLabFile,
                   csvNumFile, csvPreFile, csvLabFile,
                   numFormattedFile, preFormattedFile, dailyZipFile
            FROM {DB.SEC_REPORT_PROCESSING_TBL_NAME}
            WHERE (filingYear * 10 + (CASE
                                      WHEN filingMonth BETWEEN 1 AND 3 THEN 1
                                      WHEN filingMonth BETWEEN 4 AND 6 THEN 2
                                      WHEN filingMonth BETWEEN 7 AND 9 THEN 3
                                      ELSE 4
                                      END)) < {start_qrtr_value}
        """

        reports = self._execute_fetchall_typed(sql, ReportToCleanup)
        logging.info("Found %d reports to clean up before quarter %s", len(reports), start_qrtr_info.qrtr_string)
        return reports

    def delete_reports_before_quarter(self, start_qrtr_info: QuarterInfo) -> int:
        """
        Delete all reports with filing date before the specified quarter from the database.

        Args:
            start_qrtr_info: The starting quarter (reports before this will be deleted)

        Returns:
            Number of deleted records
        """
        # Calculate the quarter value for comparison
        start_qrtr_value = start_qrtr_info.qrtr_value

        # First, count how many records will be deleted
        count_sql = f"""
            SELECT COUNT(*) FROM {DB.SEC_REPORT_PROCESSING_TBL_NAME}
            WHERE (filingYear * 10 + (CASE
                                      WHEN filingMonth BETWEEN 1 AND 3 THEN 1
                                      WHEN filingMonth BETWEEN 4 AND 6 THEN 2
                                      WHEN filingMonth BETWEEN 7 AND 9 THEN 3
                                      ELSE 4
                                      END)) < {start_qrtr_value}
        """

        count_result = self._execute_fetchall(count_sql)
        count = count_result[0][0] if count_result else 0

        # Delete records from sec_report_processing
        delete_processing_sql = f"""
            DELETE FROM {DB.SEC_REPORT_PROCESSING_TBL_NAME}
            WHERE (filingYear * 10 + (CASE
                                      WHEN filingMonth BETWEEN 1 AND 3 THEN 1
                                      WHEN filingMonth BETWEEN 4 AND 6 THEN 2
                                      WHEN filingMonth BETWEEN 7 AND 9 THEN 3
                                      ELSE 4
                                      END)) < {start_qrtr_value}
        """

        self._execute_single(delete_processing_sql)

        # Delete records from sec_reports
        delete_reports_sql = f"""
            DELETE FROM {DB.SEC_REPORTS_TBL_NAME}
            WHERE (filingYear * 10 + (CASE
                                      WHEN filingMonth BETWEEN 1 AND 3 THEN 1
                                      WHEN filingMonth BETWEEN 4 AND 6 THEN 2
                                      WHEN filingMonth BETWEEN 7 AND 9 THEN 3
                                      ELSE 4
                                      END)) < {start_qrtr_value}
        """

        self._execute_single(delete_reports_sql)

        logging.info("Deleted %d reports from database before quarter %s", count, start_qrtr_info.qrtr_string)
        return count
