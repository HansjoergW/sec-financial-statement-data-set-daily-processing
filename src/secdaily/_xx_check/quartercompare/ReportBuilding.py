

from dataclasses import dataclass
import os
from typing import Any, Dict, List, Optional, Set

from numpy import float64, int64
import pandas as pd
from secdaily._xx_check.quartercompare.MassTestV2DataAccess import FormattedReport, QuarterFileAccess, MassTestV2DA, UpdateMassTestV2

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

@dataclass
class ReportOverview:
    totalNumAdshsDaily: Optional[int] = None
    totalNumAdshsQuarter: Optional[int] = None
    totalNumAdshsDailyOnly: Optional[int] = None
    totalNumAdshsQuarterOnly: Optional[int] = None

    totalPreAdshsDaily: Optional[int] = None
    totalPreAdshsQuarter: Optional[int] = None
    totalPreAdshsDailyOnly: Optional[int] = None
    totalPreAdshsQuarterOnly: Optional[int] = None
    
class ReportBuilder:

    def __init__(self, year: int, qrtr: int, workdir: str, run_id: int):
        self.year = year
        self.qrtr = qrtr
        self.workdir = workdir
        self.run_id = run_id
        self.qrtr_str = str(year) + "q" + str(qrtr)

        if self.workdir[-1] != '/':
            self.workdir += '/'

        self.quarter_file = self.workdir + "qrtrs/" + self.qrtr_str + ".zip"
        self.qrtr_file_access = QuarterFileAccess(self.quarter_file)

        self.mass_test_data_access = MassTestV2DA(self.workdir)

        self.adsh_daily_file_map = {}
        self.report_overview = ReportOverview()
        self.num_quarter_adshs: Set[str] = set()
        self.num_daily_adshs: Set[str] = set()
        self.pre_quarter_adshs: Set[str] = set()
        self.pre_daily_adshs:Set[str] = set()


    def _read_into_dataframes(self, files: List[str], dtypes: Dict[str, Any]) -> pd.DataFrame:
        # Use a list comprehension to read each CSV file into a DataFrame
        df_list = [pd.read_csv(file, delimiter='\t', dtype=dtypes) for file in files]

        # Concatenate all DataFrames in the list
        return pd.concat(df_list, ignore_index=True)


    def _load_daily_data(self):
        daily_reports_of_quarter:List[FormattedReport] = self.mass_test_data_access.find_entries_for_quarter(self.year, self.qrtr)

        self.adsh_daily_file_map = {x.accessionNumber: x for x in daily_reports_of_quarter}
        
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

        print("Loaded Num: ", self.daily_num_df.shape)
        print("Loaded Pre: ", self.daily_pre_df.shape)


    def _load_data(self):
        self.qrtr_file_access.load_data()
        self._load_daily_data()
        self.num_quarter_adshs = set(self.qrtr_file_access.num_df.adsh.unique().tolist())
        self.num_daily_adshs = set(self.daily_num_df.adsh.unique().tolist())

        self.pre_quarter_adshs = set(self.qrtr_file_access.pre_df.adsh.unique().tolist())
        self.pre_daily_adshs = set(self.daily_pre_df.adsh.unique().tolist())


    def _create_adsh_only_entries_quarter(self, adshs: Set[str], type: str) -> List[UpdateMassTestV2]:
        update_list = []
        for adsh in adshs:
            update_list.append(UpdateMassTestV2(runId=self.run_id, 
                                                adsh=adsh, 
                                                qtr=self.qrtr_str, 
                                                fileType=type,
                                                quarterFile=self.quarter_file,
                                                ))

        return update_list

    def _create_adsh_only_entries_daily(self, adshs: Set[str], type: str) -> List[UpdateMassTestV2]:
        update_list = []
        for adsh in adshs:
            if type == "num":
                daily_file = self.adsh_daily_file_map[adsh].numFile
            else:
                daily_file = self.adsh_daily_file_map[adsh].preFile

            update_list.append(UpdateMassTestV2(runId=self.run_id, 
                                                adsh=adsh, 
                                                qtr=self.qrtr_str, 
                                                fileType=type,
                                                dailyFile=daily_file,
                                                ))

        return update_list            

    def _compare_adshs(self) -> List[UpdateMassTestV2]:
        pre_quarter_only = self.pre_quarter_adshs - self.pre_daily_adshs
        pre_daily_only = self.pre_daily_adshs - self.pre_quarter_adshs

        num_quarter_only = self.num_quarter_adshs - self.num_daily_adshs
        num_daily_only = self.num_daily_adshs - self.num_quarter_adshs

        self.report_overview.totalNumAdshsDaily = len(self.num_daily_adshs)
        self.report_overview.totalNumAdshsQuarter = len(self.num_quarter_adshs)
        self.report_overview.totalNumAdshsDailyOnly = len(num_daily_only)
        self.report_overview.totalNumAdshsQuarterOnly = len(num_quarter_only)    

        self.report_overview.totalPreAdshsDaily = len(self.pre_daily_adshs)
        self.report_overview.totalPreAdshsQuarter = len(self.pre_quarter_adshs)
        self.report_overview.totalPreAdshsDailyOnly = len(pre_daily_only)
        self.report_overview.totalPreAdshsQuarterOnly = len(pre_quarter_only)

        # create database entries for the missing adshs as UpdateMassTestV2 objects
        update_list = []
        update_list.extend(self._create_adsh_only_entries_quarter(pre_quarter_only, "pre"))
        update_list.extend(self._create_adsh_only_entries_daily(pre_daily_only, "pre"))
        update_list.extend(self._create_adsh_only_entries_quarter(num_quarter_only, "num"))
        update_list.extend(self._create_adsh_only_entries_daily(num_daily_only, "num"))

        return update_list


    def _compare(self):
        compare_adhs_only_list = self._compare_adshs()
        self.mass_test_data_access.insert_test_result(compare_adhs_only_list)


    def report(self):
        self._load_data()
        self._compare()
        print("-----------------------------------")
        print(self.report_overview)



if __name__ == '__main__':
    from secdaily._00_common.DBBase import DB
    workdir = "d:/secprocessing2/"

    DB(workdir)._create_db()

    builder = ReportBuilder(year=2024, qrtr=4, workdir=workdir, run_id=0)
    builder.report()
