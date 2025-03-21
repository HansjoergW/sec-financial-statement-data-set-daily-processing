from dataclasses import dataclass
from typing import List
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
    fileType: str # either num or pre
    stmt: str # only for pre
    report: int
    countMatching: int
    countUnequal: int
    countOnlyOrigin: int
    countOnlyDaily: int
    tagsUnequal: str
    tagsOnlyOrigin: str
    tagsOnlyDaily: str
    quarterFile: str
    dailyFile: str


class MassTestV2DA(DB):

    months_in_qrtr = {1: [1,2,3], 2: [4,5,6], 3: [7,8,9], 4: [10,11,12]}


    def find_entries_for_quarter(self, year: int, qrtr: int) -> List[FormattedReport]:
        
        sql = f"""SELECT accessionNumber, numFormattedFile as numFile, preFormattedFile as preFile
                  FROM {DB.SEC_REPORT_PROCESSING_TBL_NAME} 
                  WHERE numFormattedFile is not NULL and preFormattedFile is not NULL
                      and filingYear = {year} and filingMonth in ({','.join([str(x) for x in self.months_in_qrtr[qrtr]])})
                  """
        return self._execute_fetchall_typed(sql, FormattedReport)


    def insert_test_result(self, update_list: List[UpdateMassTestV2]):
        sql = f"""INSERT INTO mass_test_v2 (
                           runId, adsh, qtr, fileType, stmt, report, 
                           countMatching, countUnequal, countOnlyOrigin, countOnlyDaily, 
                           tagsUnequal, tagsOnlyOrigin, tagsOnlyDaily, 
                           quarterFile, dailyFile) 
                  VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        
        self._execute_many(sql, update_list)


class QuarterFileAccess:

    def __init__(self, quarter_file: str):
        self.quarter_file = quarter_file

    def load_data(self):
        self.num_df = read_file_from_zip(self.quarter_file, 'num.txt')
        self.pre_df = read_file_from_zip(self.quarter_file, 'pre.txt')
        self.sub_df = read_file_from_zip(self.quarter_file, 'sub.txt')



if __name__ == '__main__':
    workdir = "d:/secprocessing2/"
    dbmgr = MassTestV2DA(workdir)

    entries: List[FormattedReport] = dbmgr.find_entries_for_quarter(year=2024, qrtr=4)
    print(len(entries))
