from src._00_common import DBManager
from src._01_index import SecXmlFilesProcessor

if __name__ == '__main__':
    dbm = DBManager("d:/secprocessing/")
    fileProcessor = SecXmlFilesProcessor(dbm)
    fileProcessor.downloadNumFiles()

