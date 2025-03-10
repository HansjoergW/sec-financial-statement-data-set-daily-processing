from dataclasses import dataclass
from typing import List, Optional

from secdaily._00_common.DBBase import DB


@dataclass
class MissingFile:
    accessionNumber: str
    url: str
    fileSize: str
    file: Optional[str] = None
    

class XmlFileDownloadingDA(DB):

    def find_missing_xmlNumFiles(self) -> List[MissingFile]:
        sql = '''SELECT accessionNumber, xbrlInsUrl as url, insSize as fileSize FROM {} WHERE xmlNumFile is NULL'''.format(
            DB.SEC_REPORT_PROCESSING_TBL_NAME)
        return self._execute_fetchall_typed(sql, MissingFile)

    def find_missing_xmlPreFiles(self) -> List[MissingFile]:
        sql = '''SELECT accessionNumber, xbrlPreUrl as url, preSize as fileSize FROM {} WHERE xmlPreFile is NULL'''.format(
            DB.SEC_REPORT_PROCESSING_TBL_NAME)
        return self._execute_fetchall_typed(sql, MissingFile)

    def update_processing_xml_num_file(self, update_list: List[MissingFile]):
        update_data = [(x.file, x.accessionNumber) for x in update_list]
        sql = '''UPDATE {} SET xmlNumFile = ? WHERE accessionNumber = ?'''.format(DB.SEC_REPORT_PROCESSING_TBL_NAME)
        self._execute_many(sql, update_data)

    def update_processing_xml_pre_file(self, update_list: List[MissingFile]):
        update_data = [(x.file, x.accessionNumber) for x in update_list]
        sql = '''UPDATE {} SET xmlPreFile = ? WHERE accessionNumber = ?'''.format(DB.SEC_REPORT_PROCESSING_TBL_NAME)
        self._execute_many(sql, update_data)
