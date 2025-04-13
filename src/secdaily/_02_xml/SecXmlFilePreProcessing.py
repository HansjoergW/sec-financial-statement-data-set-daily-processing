import logging
from typing import Protocol


class DataAccess(Protocol):

    def copy_uncopied_entries(self) -> int:
        """copy new entries from the report overview table to the report process table"""


class SecXmlFilePreprocessor:

    def __init__(self, dbmanager: DataAccess):
        self.dbmanager = dbmanager

    def copy_entries_to_processing_table(self):
        entries = self.dbmanager.copy_uncopied_entries()
        logging.info("%d entries copied into processing table", entries)
