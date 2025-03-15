from dataclasses import dataclass
from typing import List, Optional

from secdaily._00_common.DBBase import DB


@dataclass
class MissingFile:
    accessionNumber: str
    url: str
    fileSize: str
    file: Optional[str] = None
    type: Optional[str] = None
    

class XmlFileDownloadingDA(DB):

    def find_missing_xmlNumFiles(self) -> List[MissingFile]:
        sql = f'''SELECT accessionNumber, xbrlInsUrl as url, insSize as fileSize FROM {DB.SEC_REPORT_PROCESSING_TBL_NAME} WHERE xmlNumFile is NULL AND xbrlInsUrl IS NOT '' '''
        missings = self._execute_fetchall_typed(sql, MissingFile)

        for missing in missings:
            missing.type = 'num'
        return missings

    def find_missing_xmlPreFiles(self) -> List[MissingFile]:
        sql = f'''SELECT accessionNumber, xbrlPreUrl as url, preSize as fileSize FROM {DB.SEC_REPORT_PROCESSING_TBL_NAME} WHERE xmlPreFile is NULL AND xbrlPreUrl IS NOT '' '''
        missings = self._execute_fetchall_typed(sql, MissingFile)

        for missing in missings:
            missing.type = 'pre'
        return missings

    def find_missing_xmlLabelFiles(self) -> List[MissingFile]:
        sql = f'''SELECT accessionNumber, xbrlLabUrl as url, labSize as fileSize FROM {DB.SEC_REPORT_PROCESSING_TBL_NAME} WHERE xmlLabFile is NULL AND xbrlLabUrl IS NOT '' '''
        missings = self._execute_fetchall_typed(sql, MissingFile)    

        for missing in missings:
            missing.type = 'label'

        return missings    

    def update_processing_xml_num_file(self, update_list: List[MissingFile]):
        update_data = [(x.file, x.accessionNumber) for x in update_list]
        sql = f'''UPDATE {DB.SEC_REPORT_PROCESSING_TBL_NAME} SET xmlNumFile = ? WHERE accessionNumber = ?'''
        self._execute_many(sql, update_data)

    def update_processing_xml_pre_file(self, update_list: List[MissingFile]):
        update_data = [(x.file, x.accessionNumber) for x in update_list]
        sql = f'''UPDATE {DB.SEC_REPORT_PROCESSING_TBL_NAME} SET xmlPreFile = ? WHERE accessionNumber = ?'''
        self._execute_many(sql, update_data)

    def update_processing_xml_label_file(self, update_list: List[MissingFile]):
        update_data = [(x.file, x.accessionNumber) for x in update_list]
        sql = f'''UPDATE {DB.SEC_REPORT_PROCESSING_TBL_NAME} SET xmlLabFile = ? WHERE accessionNumber = ?'''
        self._execute_many(sql, update_data)
