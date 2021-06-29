from _00_common.DBManagement import DBManager

import logging


class SecXmlFilePreprocessor:

    def __init__(self, dbmanager: DBManager):
        self.dbmanager = dbmanager

    def copy_entries_to_processing_table(self):
        entries = self.dbmanager.copy_uncopied_entries()
        logging.info("{} entries copied into processing table".format(entries))