import logging
import os
import shutil
from pathlib import Path
from typing import List, Optional, Protocol

from secdaily._00_common.BaseDefinitions import QuarterInfo
from secdaily._00_common.ProcessBase import ProcessBase
from secdaily._06_cleanup.db.HousekeepingDataAccess import HousekeepingDataAccess, ReportToCleanup


class HousekeepingDataAccessProtocol(Protocol):
    """Protocol defining the interface for housekeeping data access."""

    def find_reports_before_quarter(self, start_qrtr_info: QuarterInfo) -> List[ReportToCleanup]:
        """Find all reports with filing date before the specified quarter."""
        return []

    def delete_reports_before_quarter(self, start_qrtr_info: QuarterInfo) -> int:
        """Delete all reports with filing date before the specified quarter from the database."""
        return 0


class Housekeeper(ProcessBase):
    """
    Class for cleaning up old data from the SEC processing pipeline.

    It can:
    1. Remove temporary files (XML, CSV, secstyle files)
    2. Remove database entries
    3. Remove quarter zip files
    4. Remove daily zip files
    """

    def __init__(
        self,
        start_qrtr_info: QuarterInfo,
        xml_dir: str,
        csv_dir: str,
        secstyle_dir: str,
        daily_zip_dir: str,
        quarter_zip_dir: str,
        db_manager: Optional[HousekeepingDataAccessProtocol] = None,
        work_dir: str = None,
    ):
        """
        Initialize the Housekeeper.

        Args:
            start_qrtr_info: The quarter to start from (data before this will be cleaned up)
            xml_dir: Directory containing XML files
            csv_dir: Directory containing CSV files
            secstyle_dir: Directory containing secstyle files
            daily_zip_dir: Directory containing daily zip files
            quarter_zip_dir: Directory containing quarter zip files
            db_manager: Database manager (optional, will create one if not provided)
            work_dir: Working directory for database (optional)
        """
        super().__init__(data_dir=work_dir or ".")

        self.start_qrtr_info = start_qrtr_info
        self.xml_dir = self._ensure_trailing_slash(xml_dir)
        self.csv_dir = self._ensure_trailing_slash(csv_dir)
        self.secstyle_dir = self._ensure_trailing_slash(secstyle_dir)
        self.daily_zip_dir = self._ensure_trailing_slash(daily_zip_dir)
        self.quarter_zip_dir = self._ensure_trailing_slash(quarter_zip_dir)

        self.db_manager = db_manager or HousekeepingDataAccess(work_dir=work_dir or ".")

    @staticmethod
    def _ensure_trailing_slash(directory: str) -> str:
        """Ensure the directory path ends with a slash."""
        if directory and directory[-1] != "/" and directory[-1] != "\\":
            return directory + "/"
        return directory

    def _is_quarter_before_start(self, qrtr_string: str) -> bool:
        """
        Check if the given quarter is before the start quarter.

        Args:
            qrtr_string: Quarter string in format 'YYYYqQ' (e.g., '2023q1')

        Returns:
            True if the quarter is before the start quarter, False otherwise
        """
        try:
            year = int(qrtr_string[:-2])
            qrtr = int(qrtr_string[-1])
            qrtr_value = year * 10 + qrtr
            return qrtr_value < self.start_qrtr_info.qrtr_value
        except (ValueError, IndexError):
            # If the format is invalid, assume it's not a quarter directory
            return False

    def cleanup_processing_files(self) -> int:
        """
        Remove temporary files (XML, CSV, secstyle files) for reports before the start quarter.

        Returns:
            Number of files removed
        """
        reports = self.db_manager.find_reports_before_quarter(self.start_qrtr_info)
        files_removed = 0

        for report in reports:
            # Remove XML files
            if report.xmlNumFile and os.path.exists(report.xmlNumFile):
                os.remove(report.xmlNumFile)
                files_removed += 1

            if report.xmlPreFile and os.path.exists(report.xmlPreFile):
                os.remove(report.xmlPreFile)
                files_removed += 1

            if report.xmlLabFile and os.path.exists(report.xmlLabFile):
                os.remove(report.xmlLabFile)
                files_removed += 1

            # Remove CSV files
            if report.csvNumFile and os.path.exists(report.csvNumFile):
                os.remove(report.csvNumFile)
                files_removed += 1

            if report.csvPreFile and os.path.exists(report.csvPreFile):
                os.remove(report.csvPreFile)
                files_removed += 1

            if report.csvLabFile and os.path.exists(report.csvLabFile):
                os.remove(report.csvLabFile)
                files_removed += 1

            # Remove secstyle files
            if report.numFormattedFile and os.path.exists(report.numFormattedFile):
                os.remove(report.numFormattedFile)
                files_removed += 1

            if report.preFormattedFile and os.path.exists(report.preFormattedFile):
                os.remove(report.preFormattedFile)
                files_removed += 1

        logging.info(
            "Removed %d processing files for quarters before %s", files_removed, self.start_qrtr_info.qrtr_string
        )
        return files_removed

    def cleanup_db_entries(self) -> int:
        """
        Remove database entries for reports before the start quarter.

        Returns:
            Number of database entries removed
        """
        return self.db_manager.delete_reports_before_quarter(self.start_qrtr_info)

    def cleanup_quarter_zip_files(self) -> int:
        """
        Remove quarter zip files for quarters before the start quarter.

        Returns:
            Number of quarter zip files removed
        """
        files_removed = 0

        if os.path.exists(self.quarter_zip_dir):
            for item in os.listdir(self.quarter_zip_dir):
                if item.endswith(".zip") and self._is_quarter_before_start(item[:-4]):
                    file_path = os.path.join(self.quarter_zip_dir, item)
                    os.remove(file_path)
                    files_removed += 1
                    logging.info("Removed quarter zip file: %s", file_path)

        logging.info(
            "Removed %d quarter zip files for quarters before %s", files_removed, self.start_qrtr_info.qrtr_string
        )
        return files_removed

    def cleanup_daily_zip_files(self) -> int:
        """
        Remove daily zip files for quarters before the start quarter.

        Returns:
            Number of daily zip files removed
        """
        dirs_removed = 0
        files_removed = 0

        if os.path.exists(self.daily_zip_dir):
            for item in os.listdir(self.daily_zip_dir):
                item_path = os.path.join(self.daily_zip_dir, item)

                # Check if it's a directory and matches the quarter format
                if os.path.isdir(item_path) and self._is_quarter_before_start(item):
                    # Count files before removing
                    files_count = sum(1 for _ in Path(item_path).glob("*.zip"))
                    files_removed += files_count

                    # Remove the entire directory
                    shutil.rmtree(item_path)
                    dirs_removed += 1
                    logging.info("Removed daily zip directory: %s containing %d files", item_path, files_count)

        logging.info(
            "Removed %d daily zip directories with %d files for quarters before %s",
            dirs_removed,
            files_removed,
            self.start_qrtr_info.qrtr_string,
        )
        return files_removed

    def process(
        self,
        remove_processing_files: bool = False,
        remove_db_entries: bool = False,
        remove_quarter_zip_files: bool = False,
        remove_daily_zip_files: bool = False,
    ) -> dict:
        """
        Perform the cleanup process based on the specified options.

        Args:
            remove_processing_files: Whether to remove temporary processing files
            remove_db_entries: Whether to remove database entries
            remove_quarter_zip_files: Whether to remove quarter zip files
            remove_daily_zip_files: Whether to remove daily zip files

        Returns:
            Dictionary with counts of removed items
        """
        logging.info("Starting cleanup for quarters before %s", self.start_qrtr_info.qrtr_string)

        result = {
            "processing_files_removed": 0,
            "db_entries_removed": 0,
            "quarter_zip_files_removed": 0,
            "daily_zip_files_removed": 0,
        }

        if remove_processing_files:
            result["processing_files_removed"] = self.cleanup_processing_files()

        if remove_db_entries:
            result["db_entries_removed"] = self.cleanup_db_entries()

        if remove_quarter_zip_files:
            result["quarter_zip_files_removed"] = self.cleanup_quarter_zip_files()

        if remove_daily_zip_files:
            result["daily_zip_files_removed"] = self.cleanup_daily_zip_files()

        logging.info("Cleanup completed for quarters before %s", self.start_qrtr_info.qrtr_string)
        return result


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d:%H:%M:%S",
        level=logging.INFO,
    )

    # Example usage
    housekeeper = Housekeeper(
        start_qrtr_info=QuarterInfo(year=2023, qrtr=1),
        xml_dir="d:/secprocessing/_1_xml/",
        csv_dir="d:/secprocessing/_2_csv/",
        secstyle_dir="d:/secprocessing/_3_secstyle/",
        daily_zip_dir="d:/secprocessing/_4_daily/",
        quarter_zip_dir="d:/secprocessing/_5_quarter/",
        work_dir="d:/secprocessing/",
    )

    result = housekeeper.process(
        remove_processing_files=True, remove_db_entries=True, remove_quarter_zip_files=True, remove_daily_zip_files=True
    )

    print(f"Cleanup results: {result}")
