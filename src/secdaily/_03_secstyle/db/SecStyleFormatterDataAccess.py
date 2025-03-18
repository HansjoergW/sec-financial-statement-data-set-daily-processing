from dataclasses import dataclass
from typing import List, Optional
from secdaily._00_common.DBBase import DB


@dataclass
class UnformattedReport:
    accessionNumber: str
    numFile: str
    preFile: str
    labFile: str


@dataclass
class UpdateStyleFormatting:
    accessionNumber: str
    formatState: str
    formatDate: str
    numFormattedFile: Optional[str]
    preFormattedFile: Optional[str]


class SecStyleFormatterDA(DB):

    def find_unformatted_reports(self) -> List[UnformattedReport]:
        sql = f"""SELECT accessionNumber, csvPreFile as preFile, csvNumFile as numFile, csvLabFile as labFile 
                  FROM {DB.SEC_REPORT_PROCESSING_TBL_NAME} 
                     WHERE numParseState is not NULL and preParseState is not NULL and labParseState is not NULL
                           and formatState is NULL
                  """
        return self._execute_fetchall_typed(sql, UnformattedReport)


    def update_formatted_reports(self, update_list: List[UpdateStyleFormatting]):
        update_data = [(x.formatState, x.formatDate, x.numFormattedFile, x.preFormattedFile, x.accessionNumber) for x in update_list]

        sql = f"""
            UPDATE {DB.SEC_REPORT_PROCESSING_TBL_NAME} 
            SET formatState = ?, formatDate = ?, numFormattedFile = ?, preFormattedFile = ?
            WHERE accessionNumber = ?
        """
        self._execute_many(sql, update_data)
