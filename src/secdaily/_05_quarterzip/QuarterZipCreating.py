"""
Module for creating quarterly zip files from daily SEC filing data. Consolidates daily zip files into quarterly
archives for efficient storage and analysis of SEC financial statement data.
"""

import logging
import os
import zipfile
from pathlib import Path
from typing import List, Optional, Set

import pandas as pd

from secdaily._00_common.BaseDefinitions import DTYPES_NUM, DTYPES_PRE, QuarterInfo, get_qrtr_string
from secdaily._00_common.ProcessBase import ProcessBase
from secdaily._00_common.SecFileUtils import read_file_from_zip


class QuarterZipCreator(ProcessBase):
    """
    This class creates quarter zip files from daily zip files.

    It handles three cases:
    1. Quarter file does not exist - create a new one from all daily zip files
    2. Quarter file exists, but new daily zip files are available - add them to the quarter file
    3. Quarter file exists and no new daily zip files are available - do nothing

    Instead of using a database to track which daily zip files are already part of the quarter file,
    it compares the file names of the daily zip files with the metadata stored in the quarter file.
    """

    def __init__(self, start_qrtr_info: QuarterInfo, daily_zip_dir: str, quarter_zip_dir: Optional[str] = None):
        """
        Initialize the QuarterZipCreator.

        Args:
            daily_zip_dir: Directory containing the daily zip files organized by quarter
            quarter_zip_dir: Directory where quarter zip files will be stored (defaults to daily_zip_dir if None)
            start_qrtr_info: The quarter to start processing from
        """
        super().__init__(data_dir=quarter_zip_dir or daily_zip_dir)

        self.daily_zip_dir = daily_zip_dir
        if self.daily_zip_dir[-1] != "/":
            self.daily_zip_dir = daily_zip_dir + "/"

        self.daily_zip_path = Path(self.daily_zip_dir)
        self.metadata_filename = "metadata.txt"
        self.start_qrtr_info = start_qrtr_info

    def _get_quarter_zip_path(self, year: int, qrtr: int) -> str:
        """
        Get the path to the quarter zip file.

        Args:
            year: The year of the quarter
            qrtr: The quarter number (1-4)

        Returns:
            The path to the quarter zip file
        """
        qrtr_str = get_qrtr_string(year, qrtr)
        return os.path.join(self.data_dir, f"{qrtr_str}.zip")

    def _get_daily_zip_files(self, year: int, qrtr: int) -> List[str]:
        """
        Get all daily zip files for a specific quarter.

        Args:
            year: The year of the quarter
            qrtr: The quarter number (1-4)

        Returns:
            List of paths to daily zip files
        """
        qrtr_str = get_qrtr_string(year, qrtr)
        qrtr_dir = os.path.join(self.daily_zip_dir, qrtr_str)

        if not os.path.exists(qrtr_dir):
            return []

        return [
            os.path.join(qrtr_dir, f)
            for f in os.listdir(qrtr_dir)
            if f.endswith(".zip") and os.path.isfile(os.path.join(qrtr_dir, f))
        ]

    def _get_processed_daily_files(self, quarter_zip_path: str) -> Set[str]:
        """
        Get the set of daily zip files that have already been processed into the quarter zip.

        Args:
            quarter_zip_path: Path to the quarter zip file

        Returns:
            Set of daily zip file names that have been processed
        """
        if not os.path.exists(quarter_zip_path):
            return set()

        try:
            with zipfile.ZipFile(quarter_zip_path, "r") as zf:
                if self.metadata_filename in zf.namelist():
                    metadata_content = zf.read(self.metadata_filename).decode("utf-8")
                    return set(line.strip() for line in metadata_content.splitlines() if line.strip())
                return set()
        except zipfile.BadZipFile:
            logging.warning("Bad zip file: %s", quarter_zip_path)
            return set()

    def _merge_dataframes(self, dfs: List[pd.DataFrame]) -> pd.DataFrame:
        """
        Merge multiple DataFrames into one, removing duplicates.

        Args:
            dfs: List of DataFrames to merge

        Returns:
            Merged DataFrame
        """
        if not dfs:
            return pd.DataFrame()

        # Filter out empty DataFrames
        non_empty_dfs = [df for df in dfs if not df.empty]
        if not non_empty_dfs:
            # If all DataFrames are empty, return an empty DataFrame with the expected columns
            # based on the first DataFrame's columns
            return pd.DataFrame(columns=dfs[0].columns)

        # Concatenate all DataFrames and drop duplicates
        result = pd.concat(non_empty_dfs, ignore_index=True)
        return result.drop_duplicates()

    def _create_quarter_zip(self, daily_zip_files: List[str], quarter_zip_path: str) -> bool:
        """
        Create a quarter zip file from daily zip files.

        Args:
            daily_zip_files: List of daily zip files to include
            quarter_zip_path: Path where the quarter zip file will be created

        Returns:
            True if successful, False otherwise
        """
        if not daily_zip_files:
            logging.info("No daily zip files found for %s", quarter_zip_path)
            return False

        try:
            # Read all sub.txt, pre.txt, and num.txt files from daily zips
            sub_dfs = []
            pre_dfs = []
            num_dfs = []

            for daily_zip in daily_zip_files:
                try:
                    sub_df = read_file_from_zip(daily_zip, "sub.txt")
                    pre_df = read_file_from_zip(daily_zip, "pre.txt", DTYPES_PRE)
                    num_df = read_file_from_zip(daily_zip, "num.txt", DTYPES_NUM)

                    sub_dfs.append(sub_df)
                    pre_dfs.append(pre_df)
                    num_dfs.append(num_df)
                except Exception as e:  # pylint: disable=broad-except
                    logging.warning("Error reading %s: %s", daily_zip, e)
                    continue

            # Merge DataFrames
            merged_sub = self._merge_dataframes(sub_dfs)
            merged_pre = self._merge_dataframes(pre_dfs)
            merged_num = self._merge_dataframes(num_dfs)

            # Create metadata content
            daily_zip_names = [os.path.basename(f) for f in daily_zip_files]
            metadata_content = "\n".join(daily_zip_names)

            # Create quarter zip file
            os.makedirs(os.path.dirname(quarter_zip_path), exist_ok=True)
            with zipfile.ZipFile(quarter_zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                zf.writestr("sub.txt", merged_sub.to_csv(sep="\t", header=True, index=False))
                zf.writestr("pre.txt", merged_pre.to_csv(sep="\t", header=True, index=False))
                zf.writestr("num.txt", merged_num.to_csv(sep="\t", header=True, index=False))
                zf.writestr(self.metadata_filename, metadata_content)

            logging.info("Created quarter zip file: %s", quarter_zip_path)
            return True

        except Exception as e:  # pylint: disable=broad-except
            logging.error("Error creating quarter zip file %s: %s", quarter_zip_path, e)
            return False

    def _update_quarter_zip(self, new_daily_zip_files: List[str], quarter_zip_path: str) -> bool:
        """
        Update an existing quarter zip file with new daily zip files.

        Args:
            new_daily_zip_files: List of new daily zip files to add
            quarter_zip_path: Path to the existing quarter zip file

        Returns:
            True if successful, False otherwise
        """
        if not new_daily_zip_files:
            logging.info("No new daily zip files to add to %s", quarter_zip_path)
            return True  # Nothing to do, but not an error

        try:
            # Read existing quarter zip content
            with zipfile.ZipFile(quarter_zip_path, "r") as zf:
                with zf.open("sub.txt") as f:
                    existing_sub = pd.read_csv(f, sep="\t", header=0)
                with zf.open("pre.txt") as f:
                    existing_pre = pd.read_csv(f, sep="\t", header=0, dtype=DTYPES_PRE)
                with zf.open("num.txt") as f:
                    existing_num = pd.read_csv(f, sep="\t", header=0, dtype=DTYPES_NUM)

                if self.metadata_filename in zf.namelist():
                    metadata_content = zf.read(self.metadata_filename).decode("utf-8")
                    processed_files = set(line.strip() for line in metadata_content.splitlines() if line.strip())
                else:
                    processed_files = set()

            # Read new daily zip content
            new_sub_dfs = [existing_sub]
            new_pre_dfs = [existing_pre]
            new_num_dfs = [existing_num]

            for daily_zip in new_daily_zip_files:
                try:
                    sub_df = read_file_from_zip(daily_zip, "sub.txt")
                    pre_df = read_file_from_zip(daily_zip, "pre.txt", DTYPES_PRE)
                    num_df = read_file_from_zip(daily_zip, "num.txt", DTYPES_NUM)

                    new_sub_dfs.append(sub_df)
                    new_pre_dfs.append(pre_df)
                    new_num_dfs.append(num_df)
                except Exception as e:  # pylint: disable=broad-except
                    logging.warning("Error reading %s: %s", daily_zip, e)
                    continue

            # Merge DataFrames
            merged_sub = self._merge_dataframes(new_sub_dfs)
            merged_pre = self._merge_dataframes(new_pre_dfs)
            merged_num = self._merge_dataframes(new_num_dfs)

            # Update metadata content
            new_daily_zip_names = [os.path.basename(f) for f in new_daily_zip_files]
            processed_files.update(new_daily_zip_names)
            updated_metadata_content = "\n".join(sorted(processed_files))

            # Create updated quarter zip file
            with zipfile.ZipFile(quarter_zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                zf.writestr("sub.txt", merged_sub.to_csv(sep="\t", header=True, index=False))
                zf.writestr("pre.txt", merged_pre.to_csv(sep="\t", header=True, index=False))
                zf.writestr("num.txt", merged_num.to_csv(sep="\t", header=True, index=False))
                zf.writestr(self.metadata_filename, updated_metadata_content)

            logging.info(
                "Updated quarter zip file: %s with %d new daily files", quarter_zip_path, len(new_daily_zip_files)
            )
            return True

        except Exception as e:  # pylint: disable=broad-except
            logging.error("Error updating quarter zip file %s: %s", quarter_zip_path, e)
            return False

    def process_quarter(self, qrtr_info: QuarterInfo) -> bool:
        """
        Process a specific quarter, creating or updating the quarter zip file as needed.

        Args:
            year: The year of the quarter
            qrtr: The quarter number (1-4)

        Returns:
            True if successful, False otherwise
        """
        year = qrtr_info.year
        qrtr = qrtr_info.qrtr

        quarter_zip_path = self._get_quarter_zip_path(year, qrtr)
        daily_zip_files = self._get_daily_zip_files(year, qrtr)

        if not daily_zip_files:
            logging.info("No daily zip files found for %dQ%d", year, qrtr)
            return True  # Nothing to do, but not an error

        # Check if quarter zip exists
        if not os.path.exists(quarter_zip_path):
            # Case 1: Quarter file does not exist
            return self._create_quarter_zip(daily_zip_files, quarter_zip_path)

        # Get processed daily files
        processed_files = self._get_processed_daily_files(quarter_zip_path)

        # Find new daily zip files
        new_daily_zip_files = [f for f in daily_zip_files if os.path.basename(f) not in processed_files]

        if not new_daily_zip_files:
            # Case 3: Quarter file exists and no new daily zip files
            logging.info("No new daily zip files for %dQ%d", year, qrtr)
            return True

        # Case 2: Quarter file exists and new daily zip files are available
        return self._update_quarter_zip(new_daily_zip_files, quarter_zip_path)

    def process(self):
        """
        Process all quarters found in the daily zip directory.
        """
        logging.info("Quarter zip creating")

        # Find all quarter directories in the daily zip directory
        quarters: List[QuarterInfo] = []
        for item in os.listdir(self.daily_zip_dir):
            if (
                os.path.isdir(os.path.join(self.daily_zip_dir, item))
                and item.endswith("q1")
                or item.endswith("q2")
                or item.endswith("q3")
                or item.endswith("q4")
            ):
                try:
                    year = int(item[:-2])
                    qrtr = int(item[-1])
                    quarters.append(QuarterInfo(year=year, qrtr=qrtr))
                except ValueError:
                    continue

        # filter only quarters that are equal or later than the start quarter
        quarters = [qrtr for qrtr in quarters if qrtr.qrtr_value >= self.start_qrtr_info.qrtr_value]

        if not quarters:
            logging.info("No quarter directories to process")
            return

        # Process each quarter
        for quarter in quarters:
            self.process_quarter(quarter)


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d:%H:%M:%S",
        level=logging.DEBUG,
    )

    # Example usage
    creator = QuarterZipCreator(
        start_qrtr_info=QuarterInfo(),
        daily_zip_dir="d:/secprocessing2/_4_daily/",
        quarter_zip_dir="d:/secprocessing2/_5_quarter/",
    )
    creator.process()
