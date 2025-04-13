from dataclasses import dataclass
from typing import List, Optional

from secdaily._00_common.BaseDefinitions import get_qrtr_string_by_month
from secdaily._00_common.DBBase import DB


@dataclass
class UnformattedReport:
    accessionNumber: str
    numFile: str
    preFile: str
    labFile: str
    filingDay: int
    filingMonth: int
    filingYear: int

    def get_qrtr_string(self) -> str:
        return get_qrtr_string_by_month(self.filingYear, self.filingMonth)

    def get_filing_date(self) -> str:
        return f"{self.filingYear}-{self.filingMonth}-{self.filingDay}"


@dataclass
class UpdateStyleFormatting:
    accessionNumber: str
    formatState: str
    formatDate: str
    numFormattedFile: Optional[str]
    preFormattedFile: Optional[str]


class SecStyleFormatterDA(DB):

    def find_unformatted_reports(self) -> List[UnformattedReport]:
        sql = f"""SELECT accessionNumber, csvPreFile as preFile, csvNumFile as numFile, csvLabFile as labFile,
                         filingDay, filingMonth, filingYear
                  FROM {DB.SEC_REPORT_PROCESSING_TBL_NAME}
                     WHERE     numParseState is not NULL and preParseState is not NULL and labParseState is not NULL
                           and csvNumFile is not NULL and csvPreFile is not NULL and csvLabFile is not NULL
                           and formatState is NULL
                  """
        return self._execute_fetchall_typed(sql, UnformattedReport)

    def update_formatted_reports(self, update_list: List[UpdateStyleFormatting]):
        update_data = [
            (x.formatState, x.formatDate, x.numFormattedFile, x.preFormattedFile, x.accessionNumber)
            for x in update_list
        ]

        sql = f"""
            UPDATE {DB.SEC_REPORT_PROCESSING_TBL_NAME}
            SET formatState = ?, formatDate = ?, numFormattedFile = ?, preFormattedFile = ?
            WHERE accessionNumber = ?
        """
        self._execute_many(sql, update_data)
