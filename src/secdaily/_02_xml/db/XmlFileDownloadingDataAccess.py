from dataclasses import dataclass
from typing import List, Optional

from secdaily._00_common.BaseDefinitions import get_qrtr_string_by_month
from secdaily._00_common.DBBase import DB


@dataclass
class MissingFile:
    accessionNumber: str
    url: str
    fileSize: str
    filingDay: int
    filingMonth: int
    filingYear: int
    file: Optional[str] = None
    type: Optional[str] = None

    def get_qrtr_string(self) -> str:
        return get_qrtr_string_by_month(self.filingYear, self.filingMonth)

    def get_filing_date(self) -> str:
        return f"{self.filingYear}-{self.filingMonth}-{self.filingDay}"


class XmlFileDownloadingDA(DB):

    def find_missing_xmlNumFiles(self) -> List[MissingFile]:
        sql = f"""SELECT accessionNumber, filingDay, filingMonth, filingYear, xbrlInsUrl as url, insSize as fileSize
                  FROM {DB.SEC_REPORT_PROCESSING_TBL_NAME}
                  WHERE xmlNumFile is NULL AND xbrlInsUrl IS NOT '' """
        missings = self._execute_fetchall_typed(sql, MissingFile)

        for missing in missings:
            missing.type = "num"
        return missings

    def find_missing_xmlPreFiles(self) -> List[MissingFile]:
        sql = f"""SELECT accessionNumber, filingDay, filingMonth, filingYear,xbrlPreUrl as url, preSize as fileSize
                  FROM {DB.SEC_REPORT_PROCESSING_TBL_NAME}
                  WHERE xmlPreFile is NULL AND xbrlPreUrl IS NOT '' """
        missings = self._execute_fetchall_typed(sql, MissingFile)

        for missing in missings:
            missing.type = "pre"
        return missings

    def find_missing_xmlLabelFiles(self) -> List[MissingFile]:
        sql = f"""SELECT accessionNumber, filingDay, filingMonth, filingYear, xbrlLabUrl as url, labSize as fileSize
                  FROM {DB.SEC_REPORT_PROCESSING_TBL_NAME}
                  WHERE xmlLabFile is NULL AND xbrlLabUrl IS NOT '' """
        missings = self._execute_fetchall_typed(sql, MissingFile)

        for missing in missings:
            missing.type = "label"

        return missings

    def update_processing_xml_num_file(self, update_list: List[MissingFile]):
        update_data = [(x.file, x.accessionNumber) for x in update_list]
        sql = f"""UPDATE {DB.SEC_REPORT_PROCESSING_TBL_NAME} SET xmlNumFile = ? WHERE accessionNumber = ?"""
        self._execute_many(sql, update_data)

    def update_processing_xml_pre_file(self, update_list: List[MissingFile]):
        update_data = [(x.file, x.accessionNumber) for x in update_list]
        sql = f"""UPDATE {DB.SEC_REPORT_PROCESSING_TBL_NAME} SET xmlPreFile = ? WHERE accessionNumber = ?"""
        self._execute_many(sql, update_data)

    def update_processing_xml_label_file(self, update_list: List[MissingFile]):
        update_data = [(x.file, x.accessionNumber) for x in update_list]
        sql = f"""UPDATE {DB.SEC_REPORT_PROCESSING_TBL_NAME} SET xmlLabFile = ? WHERE accessionNumber = ?"""
        self._execute_many(sql, update_data)
