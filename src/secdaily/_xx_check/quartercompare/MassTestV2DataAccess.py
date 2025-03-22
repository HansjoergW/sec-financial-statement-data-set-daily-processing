from dataclasses import dataclass
from typing import List, Optional
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
    stmt: Optional[str] = None # only for pre
    report: Optional[int] = None # only for pre
    countMatching: Optional[int] = None
    countUnequal: Optional[int] = None
    countOnlyOrigin: Optional[int] = None
    countOnlyDaily: Optional[int] = None
    tagsUnequal: Optional[str] = None
    tagsOnlyOrigin: Optional[str] = None
    tagsOnlyDaily: Optional[str] = None
    quarterFile: Optional[str] = None
    dailyFile: Optional[str] = None


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
        sql = f"""INSERT INTO {DB.MASS_TESTING_V2_TBL_NAME} 
                    (runId, adsh, qtr, fileType, stmt, report, 
                     countMatching, countUnequal, countOnlyOrigin, countOnlyDaily, 
                     tagsUnequal, tagsOnlyOrigin, tagsOnlyDaily, quarterFile, dailyFile) 
                     VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

        # Konvertiere UpdateMassTestV2 Objekte in Tupel
        params = [(
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
            update.dailyFile
        ) for update in update_list]
        
        self._execute_many(sql, params)


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
