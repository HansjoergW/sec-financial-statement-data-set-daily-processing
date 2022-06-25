from _00_common.DBManagement import DBManager, XbrlFile, XbrlFiles, BasicFeedData
from _00_common.SecFileUtils import get_url_content
from _00_common.ParallelExecution import ParallelExecutor

from typing import Dict, List, Protocol

import json
import logging


class DataAccessor(Protocol):

    def read_last_known_fiscalyearend(self) -> Dict[str, str]:
        """ reads the last known fiscalYearValue per cik from its 10-K reports"""

    def find_entries_with_missing_xbrl_ins_or_pre(self) -> List[BasicFeedData]:
        """ select entries for which the urls for there ins and pre xbrl files are not known """

    def update_xbrl_infos(self, xbrlfiles: List[XbrlFiles]):
        """ update the information for th xbrl files in an entry """

    def find_duplicated_adsh(self) -> List[str]:
        """ find entries which have the same accessionNumber """

    def mark_duplicated_adsh(self, adsh: str):
        """ mark duplicated entries """


class SecFullIndexFilePostProcessor:
    """
    - parses the index.json file for every report in order to find the name of the main report xbrl files
    - adds this information to the db
    """

    edgar_archive_root_url = "https://www.sec.gov/Archives/"

    def __init__(self, dbmanager: DataAccessor):
        self.dbmanager = dbmanager

        # read that last known fye day/month values
        self.last_knwon_fye_dict: Dict[str, str] = self.dbmanager.read_last_known_fiscalyearend()

    def _find_xbrl_files(self, rowdata: BasicFeedData) -> XbrlFiles:
        report_path = rowdata.reportJson[:rowdata.reportJson.rfind('/') + 1]

        index_json_url = SecFullIndexFilePostProcessor.edgar_archive_root_url + rowdata.reportJson

        try:
            content = get_url_content(index_json_url)
            json_content = json.loads(content)
            relevant_entries: Dict[str, XbrlFile] = {}
            for fileentry in json_content['directory']['item']:
                name = fileentry['name']

                if (name.endswith("-xbrl.zip") | name.endswith(".xml")):
                    last_modified = fileentry['last-modified']
                    size = fileentry['size']
                    try:
                        size = int(size)
                    except ValueError:
                        size = 0  # the default value

                    key = name
                    if name.endswith('-xbrl.zip'):
                        key = 'xbrlzip'
                    if name.endswith('_cal.xml'):
                        key = 'cal'
                    if name.endswith('_def.xml'):
                        key = 'def'
                    if name.endswith('_lab.xml'):
                        key = 'lab'
                    if name.endswith('_pre.xml'):
                        key = 'pre'
                    if name.endswith('_htm.xml'):
                        key = 'ins'

                    relevant_entries[key] = XbrlFile(name,
                                                     SecFullIndexFilePostProcessor.edgar_archive_root_url + report_path + name,
                                                     last_modified, size)

            if 'ins' not in relevant_entries:
                ins_file = relevant_entries['pre'].name.replace("_pre", "")
                relevant_entries['ins'] = relevant_entries[ins_file]

            period = relevant_entries['pre'].name.replace("_pre.xml", "")[-8:]

            # if we have a 10-K, the fye is the month and date of the period
            if rowdata.formType is "10-K":
                fiscal_year_end = period[-4:]
            else:  # 10-Q
                # otherwise we try to map it from entries we found in our database (which will be in general the
                # fye of the last former 10-K)
                fiscal_year_end = self.last_knwon_fye_dict.get(rowdata.cikNumber, None)

            return XbrlFiles(accessionNumber=rowdata.accessionNumber,
                             sec_feed_file=rowdata.sec_feed_file,
                             fiscal_year_end=fiscal_year_end,
                             period=period,
                             xbrlIns=relevant_entries['ins'], xbrlPre=relevant_entries['pre'],
                             xbrlCal=relevant_entries['cal'], xbrlDef=relevant_entries['def'],
                             xbrlLab=relevant_entries['lab'], xbrlZip=relevant_entries['xbrlzip'])

        except:
            return XbrlFiles(rowdata.accessionNumber, rowdata.sec_feed_file, None, None, None, None, None, None, None,
                             None)

    def process(self):
        executor = ParallelExecutor[BasicFeedData, XbrlFiles, type(None)](max_calls_per_sec=8)

        executor.set_get_entries_function(self.dbmanager.find_entries_with_missing_xbrl_ins_or_pre)
        executor.set_process_element_function(self._find_xbrl_files)
        executor.set_post_process_chunk_function(self.dbmanager.update_xbrl_infos)

        _, unprocessed = executor.execute()
        if len(unprocessed) > 0:
            unprocessed_adshs = [x.accessionNumber for x in unprocessed]
            logging.info(f"failed to process {','.join(unprocessed_adshs)}")

    def check_for_duplicated(self):
        duplicated_adshs: List[str] = self.dbmanager.find_duplicated_adsh()
        for duplicated in duplicated_adshs:
            logging.info("Found duplicated: " + duplicated)
            self.dbmanager.mark_duplicated_adsh(duplicated)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.DEBUG)

    folder = "./tmp"
    # new_dbmgr = DBManager(work_dir=folder)
    # new_dbmgr._create_db()
    new_dbmgr = DBManager(work_dir="d:/secprocessing/")
    processor = SecFullIndexFilePostProcessor(new_dbmgr)
    processor.process()

    # dbm = DBManager(work_dir="d:/secprocessing/")
    # lastye: Dict[str, str] = dbm.read_last_known_fiscalyearend()
    #
    # conn = dbm.get_connection()
    # sql = '''SELECT accessionNumber, cikNumber FROM sec_feeds WHERE fiscalYearEnd is null'''
    # results = conn.execute(sql).fetchall()
    #
    # mapped = [(lastye.get(x[1], None), x[0]) for x in results]
    #
    # found = [x for x in mapped if x[0] is not None]
    # not_found = [x for x in mapped if x[0] is None]
    # conn.close()
    #
    # conn = dbm.get_connection()
    # sql = '''UPDATE sec_feeds SET fiscalYearEnd = ? WHERE accessionNumber = ?'''
    # conn.executemany(sql, found)
    # conn.commit()
    # conn.close()
    #
    # print("found: ", len(found))
    # print("not found: ", len(not_found))

# adsh = None
# report_index_json_url = test_reports[1]
# SecFullIndexFilePostProcessor._find_xbrl_files((adsh, None, None, None, None, report_index_json_url))
