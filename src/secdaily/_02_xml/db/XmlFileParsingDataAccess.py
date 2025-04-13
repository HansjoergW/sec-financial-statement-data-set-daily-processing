from dataclasses import dataclass
from typing import List, Optional

from secdaily._00_common.BaseDefinitions import get_qrtr_string_by_month
from secdaily._00_common.DBBase import DB


@dataclass
class UnparsedFile:
    accessionNumber: str
    file: str
    filingDay: int
    filingMonth: int
    filingYear: int

    def get_qrtr_string(self) -> str:
        return get_qrtr_string_by_month(self.filingYear, self.filingMonth)

    def get_filing_date(self) -> str:
        return f"{self.filingYear}-{self.filingMonth}-{self.filingDay}"


@dataclass
class UpdateNumParsing:
    accessionNumber: str
    csvNumFile: Optional[str]
    numParseDate: str
    numParseState: str
    fiscalYearEnd: Optional[str]


@dataclass
class UpdatePreParsing:
    accessionNumber: str
    csvPreFile: Optional[str]
    preParseDate: str
    preParseState: str


@dataclass
class UpdateLabParsing:
    accessionNumber: str
    csvLabFile: Optional[str]
    labParseDate: str
    labParseState: str


class XmlFileParsingDA(DB):

    def find_unparsed_numFiles(self) -> List[UnparsedFile]:
        sql = f"""SELECT accessionNumber, xmlNumFile as file, filingDay, filingMonth, filingYear
                  FROM {DB.SEC_REPORT_PROCESSING_TBL_NAME}
                  WHERE xmlNumFile is not NULL and csvNumFile is NULL and numParseState is NULL"""
        return self._execute_fetchall_typed(sql, UnparsedFile)

    def find_unparsed_preFiles(self) -> List[UnparsedFile]:
        sql = f"""SELECT accessionNumber, xmlPreFile as file, filingDay, filingMonth, filingYear
                  FROM {DB.SEC_REPORT_PROCESSING_TBL_NAME}
                  WHERE xmlPreFile is not NULL and csvPreFile is NULL and preParseState is NULL"""
        return self._execute_fetchall_typed(sql, UnparsedFile)

    def find_unparsed_labFiles(self) -> List[UnparsedFile]:
        sql = f"""SELECT accessionNumber, xmlLabFile as file, filingDay, filingMonth, filingYear
                  FROM {DB.SEC_REPORT_PROCESSING_TBL_NAME}
                  WHERE xmlLabFile is not NULL and csvLabFile is NULL and labParseState is NULL"""
        return self._execute_fetchall_typed(sql, UnparsedFile)

    def update_parsed_num_file(self, updatelist: List[UpdateNumParsing]):
        update_data = [
            (x.csvNumFile, x.numParseDate, x.numParseState, x.fiscalYearEnd, x.accessionNumber) for x in updatelist
        ]

        sql = f"""UPDATE {DB.SEC_REPORT_PROCESSING_TBL_NAME}
                  SET csvNumFile = ?, numParseDate = ?, numParseState = ?, fiscalYearEnd =? WHERE accessionNumber = ?"""
        self._execute_many(sql, update_data)

    def update_parsed_pre_file(self, updatelist: List[UpdatePreParsing]):
        update_data = [(x.csvPreFile, x.preParseDate, x.preParseState, x.accessionNumber) for x in updatelist]

        sql = f"""UPDATE {DB.SEC_REPORT_PROCESSING_TBL_NAME} SET csvPreFile = ?, preParseDate = ?, preParseState = ?
                  WHERE accessionNumber = ?"""
        self._execute_many(sql, update_data)

    def update_parsed_lab_file(self, updatelist: List[UpdateLabParsing]):
        update_data = [(x.csvLabFile, x.labParseDate, x.labParseState, x.accessionNumber) for x in updatelist]

        sql = f"""UPDATE {DB.SEC_REPORT_PROCESSING_TBL_NAME} SET csvLabFile = ?, labParseDate = ?, labParseState = ?
                  WHERE accessionNumber = ?"""
        self._execute_many(sql, update_data)
