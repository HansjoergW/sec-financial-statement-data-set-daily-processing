

import os
from typing import Any, Dict, List

from numpy import float64, int64
import pandas as pd
from secdaily._xx_check.quartercompare.MassTestV2DataAccess import FormattedReport, QuarterFileAccess, MassTestV2DA

DTYPES_NUM =  {
        'adsh': str,
        'tag': str,
        'version': str,
        'ddate': int64,
        'qtrs': int,
        'uom': str,
        'coreg': str,
        'value': float64,
        'footnote': str, 
        'segments': str
    }

DTYPES_PRE = {
        'adsh': str,
        'stmt': str,
        'tag': str,
        'version': str,
        'line': int,
        'report': int,
        'negating': bool,
        'plabel': str
    }


class ReportBuilder:

    def __init__(self, year: int, qrtr: int, workdir: str):
        self.year = year
        self.qrtr = qrtr
        self.workdir = workdir

        if self.workdir[-1] != '/':
            self.workdir += '/'

        self.quarter_file = self.workdir + "qrtrs/" + str(year) + "q" + str(qrtr) + ".zip"
        self.qrtr_file_access = QuarterFileAccess(self.quarter_file)

        self.mass_test_data_access = MassTestV2DA(self.workdir)


    def _read_into_dataframes(self, files: List[str], dtypes: Dict[str, Any]) -> pd.DataFrame:
        # Use a list comprehension to read each CSV file into a DataFrame
        df_list = [pd.read_csv(file, delimiter='\t', dtype=dtypes) for file in files]

        # Concatenate all DataFrames in the list
        return pd.concat(df_list, ignore_index=True)


    def _load_daily_data(self):
        daily_reports_of_quarter:List[FormattedReport] = self.mass_test_data_access.find_entries_for_quarter(self.year, self.qrtr)

        daily_num_files = [f"{x.numFile}.zip" for x in daily_reports_of_quarter]
        daily_pre_files = [f"{x.preFile}.zip" for x in daily_reports_of_quarter]

        num_parquet_file = self.workdir + "qrtrs/daily_num.parquet"
        pre_parquet_file = self.workdir + "qrtrs/daily_pre.parquet"

        print("loading daily num files: ", len(daily_num_files))       
        if os.path.exists(num_parquet_file):
            print(" ... from parquet")
            self.daily_num_df = pd.read_parquet(num_parquet_file)
        else:            
            self.daily_num_df = self._read_into_dataframes(daily_num_files, DTYPES_NUM)
            self.daily_num_df.to_parquet(self.workdir + "qrtrs/daily_num.parquet")

        print("loading daily pre files: ", len(daily_pre_files))
        if os.path.exists(pre_parquet_file):
            print(" ... from parquet")
            self.daily_pre_df = pd.read_parquet(pre_parquet_file)
        else:
            self.daily_pre_df = self._read_into_dataframes(daily_pre_files, DTYPES_PRE)
            self.daily_pre_df.to_parquet(self.workdir + "qrtrs/daily_pre.parquet")


    def _load_data(self):
        self.qrtr_file_access.load_data()
        self._load_daily_data()


    def report(self):
        self._load_data()
        print(self.daily_num_df.shape)
        print(self.daily_pre_df.shape)
        print("------")



if __name__ == '__main__':
    workdir = "d:/secprocessing2/"
    builder = ReportBuilder(2024, 4, workdir)
    builder.report()
