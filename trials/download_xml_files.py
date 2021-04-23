from _00_common.DBManagement import DBManager
from _02_xml.SecFilesProcessing import SecXmlFilesProcessor

if __name__ == '__main__':
    dbm = DBManager("d:/secprocessing/")
    fileProcessor = SecXmlFilesProcessor(dbm)
    fileProcessor.downloadNumFiles()

