from dataclasses import dataclass
from typing import List, Optional

from secdaily._00_common.DBBase import DB


@dataclass
class UnparsedFile:
    accessionNumber: str
    file: str


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


class XmlFileParsingDA(DB):

    def find_unparsed_numFiles(self) -> List[UnparsedFile]:
        sql = '''SELECT accessionNumber, xmlNumFile as file FROM {} WHERE csvNumFile is NULL and numParseState is NULL'''.format(
            DB.SEC_REPORT_PROCESSING_TBL_NAME)
        return self._execute_fetchall_typed(sql, UnparsedFile)

    def find_unparsed_preFiles(self) -> List[UnparsedFile]:
        sql = '''SELECT accessionNumber, xmlPreFile as file FROM {} WHERE csvPreFile is NULL and preParseState is NULL'''.format(
            DB.SEC_REPORT_PROCESSING_TBL_NAME)
        return self._execute_fetchall_typed(sql, UnparsedFile)

    def update_parsed_num_file(self, updatelist: List[UpdateNumParsing]):
        update_data = [(x.csvNumFile, x.numParseDate, x.numParseState, x.fiscalYearEnd, x.accessionNumber) for x in
                       updatelist]

        sql = '''UPDATE {} SET csvNumFile = ?, numParseDate = ?, numParseState = ?, fiscalYearEnd =? WHERE accessionNumber = ?'''.format(
            DB.SEC_REPORT_PROCESSING_TBL_NAME)
        self._execute_many(sql, update_data)

    def update_parsed_pre_file(self, updatelist: List[UpdatePreParsing]):
        update_data = [(x.csvPreFile, x.preParseDate, x.preParseState, x.accessionNumber) for x in updatelist]

        sql = '''UPDATE {} SET csvPreFile = ?, preParseDate = ?, preParseState = ? WHERE accessionNumber = ?'''.format(
            DB.SEC_REPORT_PROCESSING_TBL_NAME)
        self._execute_many(sql, update_data)