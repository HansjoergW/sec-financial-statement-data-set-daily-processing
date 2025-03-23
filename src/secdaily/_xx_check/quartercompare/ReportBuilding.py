

from dataclasses import dataclass
import os
from typing import Any, Dict, List, Optional, Set

from numpy import equal, float64, int64
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

        self.pre_both_adshs: Set[str] = set()
        self.num_both_adshs: Set[str] = set()


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
        self.num_both_adshs = self.num_quarter_adshs & self.num_daily_adshs
        

        self.pre_quarter_adshs = set(self.qrtr_file_access.pre_df.adsh.unique().tolist())
        self.pre_daily_adshs = set(self.daily_pre_df.adsh.unique().tolist())
        self.pre_both_adshs = self.pre_quarter_adshs & self.pre_daily_adshs


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


    def _compare_dataframes(self, left_df: pd.DataFrame, right_df: pd.DataFrame) -> pd.DataFrame:
        # Ensure both dataframes have the same columns
        common_columns = list(set(left_df.columns) & set(right_df.columns))
        left_df = left_df[common_columns]
        right_df = right_df[common_columns]

        # Add a 'compare' column to both dataframes
        left_df['compare'] = 'in left'
        right_df['compare'] = 'in right'

        # Concatenate the dataframes
        combined_df = pd.concat([left_df, right_df], axis=0)

        # Find duplicates (rows that appear in both dataframes)
        duplicates = combined_df.duplicated(subset=common_columns, keep=False)

        # Mark duplicates as 'in both'
        combined_df.loc[duplicates, 'compare'] = 'in both'

        # Remove duplicate rows, keeping one instance
        result_df = combined_df.drop_duplicates(subset=common_columns, keep='first')

        return result_df

    def _create_update_entry(self, compare_results: pd.DataFrame, adsh: str, stmt: Optional[str] = None) -> UpdateMassTestV2:
        equal_count = compare_results[compare_results.compare == 'in both'].shape[0]

        left_only = compare_results[compare_results.compare == 'in left']
        right_only = compare_results[compare_results.compare == 'in right']

        left_only_marked_tags = set(left_only.tag.unique().tolist())
        right_only_marked_tags = set(right_only.tag.unique().tolist())
        
        unequal_tags = left_only_marked_tags.intersection(right_only_marked_tags)
        left_only_tags = list(left_only_marked_tags - unequal_tags)
        right_only_tags = list(right_only_marked_tags - unequal_tags)

        unequal_count = len(unequal_tags)
        left_count = len(left_only_tags)
        right_count = len(right_only_tags)
                        
        
        updated_entry = UpdateMassTestV2(runId=self.run_id, 
                                            adsh=adsh, 
                                            qtr=self.qrtr_str, 
                                            fileType="pre",
                                            stmt=stmt,
                                            countMatching=equal_count,
                                            countUnequal=unequal_count,
                                            countOnlyOrigin=left_count,
                                            countOnlyDaily=right_count,
                                            tagsUnequal=", ".join(unequal_tags),
                                            tagsOnlyOrigin=", ".join(left_only_tags),
                                            tagsOnlyDaily=", ".join(right_only_tags),
                                            quarterFile=self.quarter_file,
                                            dailyFile=self.adsh_daily_file_map[adsh].preFile,
                                            )
        return updated_entry
     

    def _compare_pre(self) -> List[UpdateMassTestV2]:
        cols = ['adsh', 'stmt', 'tag', 'version', 'line', 'negating', 'plabel']

        update_list = []
        for adsh in self.pre_both_adshs:
            quarter_df = self.qrtr_file_access.pre_df[self.qrtr_file_access.pre_df.adsh == adsh]
            daily_df = self.daily_pre_df[self.daily_pre_df.adsh == adsh]

            stmts = set(quarter_df.stmt.unique().tolist() + daily_df.stmt.unique().tolist())
            for stmt in stmts:
                quarter_stmt_df = quarter_df[quarter_df.stmt == stmt]
                daily_stmt_df = daily_df[daily_df.stmt == stmt]
                compare_results = self._compare_dataframes(quarter_stmt_df[cols], daily_stmt_df[cols])
                updated_entry = self._create_update_entry(compare_results, adsh, stmt)
                update_list.append(updated_entry)
        return update_list


    def _compare_num(self) -> List[UpdateMassTestV2]:
        cols = ['adsh', 'tag', 'version', 'ddate', 'qtrs', 'coreg', 'uom', 'value', 'segments', 'footnote']
        update_list = []
        for adsh in self.num_both_adshs:
            quarter_df = self.qrtr_file_access.num_df[self.qrtr_file_access.num_df.adsh == adsh]
            daily_df = self.daily_num_df[self.daily_num_df.adsh == adsh]
            compare_results = self._compare_dataframes(quarter_df[cols], daily_df[cols])
            updated_entry = self._create_update_entry(compare_results, adsh)
            update_list.append(updated_entry)
        return update_list


    def _compare(self):
        change_list: List[UpdateMassTestV2] = []
        change_list.extend(self._compare_adshs())
        change_list.extend(self._compare_pre())
        change_list.extend(self._compare_num())

        self.mass_test_data_access.insert_test_result(change_list)


    def report(self):
        self._load_data()
        self._compare()
        print("-----------------------------------")
        print(self.report_overview)



if __name__ == '__main__':
    from secdaily._00_common.DBBase import DB
    workdir = "d:/secprocessing2/"

    DB(workdir)._create_db()

    builder = ReportBuilder(year=2024, qrtr=4, workdir=workdir, run_id=1)
    builder.report()
