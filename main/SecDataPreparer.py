from _00_common.DBManagement import DBManager
from _02_xml.SecFilesProcessing import  SecFilesProcessor
from _02_xml.SecFeedDataManagement import SecFeedDataManager


class SecProcessingOrchestrator():

    def __init__(self, workdir: str):
        self.workdir = workdir
        self.feeddir = workdir + "feed/"
        self.dbmanager = DBManager(work_dir=workdir)
        self.secfeeddatamgr = SecFeedDataManager(self.dbmanager)

    def process_sec_feed_data(self):
        secfilesprocessor = SecFilesProcessor(self.dbmanager, 2020, 2021, 10, 2, self.feeddir)
        secfilesprocessor.download_sec_feeds()

    def complete_sec_feed_data(self):
        self.secfeeddatamgr.add_missing_xbrlinsurl()


if __name__ == '__main__':
    workdir_default = "d:/secprocessing/"
    orchestrator = SecProcessingOrchestrator(workdir_default)
    orchestrator.process_sec_feed_data()
    orchestrator.complete_sec_feed_data()
