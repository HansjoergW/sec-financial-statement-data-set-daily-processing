from _00_common.DBManagement import DBManager
from _01_index.SecIndexFileProcessing import SecXmlFilesProcessor

if __name__ == '__main__':
    dbm = DBManager("d:/secprocessing/")
    fileProcessor = SecXmlFilesProcessor(dbm)
    fileProcessor.downloadNumFiles()

