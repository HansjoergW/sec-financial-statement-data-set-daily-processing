from _00_common.DBManagement import DBManager, XbrlFile, XbrlFiles
from _00_common.SecFileUtils import get_url_content

from time import time, sleep
from multiprocessing import Pool
from typing import Dict, List, Tuple, Optional

from dataclasses import dataclass, field, asdict

import json
import logging

class SecFullIndexFilePostProcessor:
    """
    - parses the index.json file for every report in order to find the name of the main report xbrl files
    - adds this information to the db
    """

    edgar_archive_root_url = "https://www.sec.gov/Archives/"

    def __init__(self, dbmanager: DBManager):
        self.dbmanager = dbmanager

    @staticmethod
    def _find_xbrl_files(data: Tuple[str, str, str, str, str]) -> XbrlFiles:
        adsh = data[0]
        sec_feed_file = data[1]
        report_json = data[4]
        report_path = report_json[:report_json.rfind('/') + 1]

        index_json_url = SecFullIndexFilePostProcessor.edgar_archive_root_url + report_json

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

                    relevant_entries[key] = XbrlFile(name, SecFullIndexFilePostProcessor.edgar_archive_root_url + report_path + name, last_modified, size)

            if 'ins' not in relevant_entries:
                ins_file = relevant_entries['pre'].name.replace("_pre", "")
                relevant_entries['ins'] = relevant_entries[ins_file]

            period = relevant_entries['pre'].name.replace("_pre.xml", "")[-8:]

            return XbrlFiles(adsh, sec_feed_file, period,
                             relevant_entries['ins'], relevant_entries['pre'],
                             relevant_entries['cal'], relevant_entries['def'],
                             relevant_entries['lab'], relevant_entries['xbrlzip'])

        except:
            return XbrlFiles(adsh, sec_feed_file, None, None, None, None, None, None, None)

    @staticmethod
    def _find_main_file_throttle(data_tuple: Tuple[str, str, str, str, str]) -> XbrlFiles:
        # ensures that only one request per second is send
        start = time()
        xbrlfiles: XbrlFiles = SecFullIndexFilePostProcessor._find_xbrl_files(data_tuple)
        end = time()
        sleep((1000-(end - start)) / 1000)
        return xbrlfiles

    def complete_xbrl_file_information(self):
        # das nächste problem ist es die Namen der Dateien zu finden, das geht nur über
        # einen zusätzlices laden der json index datei pro report..
        # das müsste dann wieder parallel gemacht werden.
        pool = Pool(8)

        last_missing: int = None
        missing: List[Tuple[str, str, str, str, str]] = self.dbmanager.find_entries_with_missing_xbrl_ins_or_pre()
        while (last_missing is None) or (last_missing > len(missing)):
            last_missing = len(missing)
            logging.info("missing entries " + str(len(missing)))

            for i in range(0, len(missing), 100):
                chunk = missing[i:i + 100]
                update_data: List[XbrlFiles] = pool.map(SecFullIndexFilePostProcessor._find_main_file_throttle, chunk)
                self.dbmanager.update_xbrl_infos(update_data)
                logging.info("commited chunk: " + str(i))

            missing = self.dbmanager.find_entries_with_missing_xbrl_ins_or_pre()

        if len(missing) > 0:
            logging.info("Failed to add missing for " + str(len(missing)))

    def process(self):
        self.complete_xbrl_file_information()

    def check_for_duplicated(self):
        duplicated_adshs: List[str] = self.dbmanager.find_duplicated_adsh()
        for duplicated in duplicated_adshs:
            logging.info("Found duplicated: " + duplicated)
            self.dbmanager.mark_duplicated_adsh(duplicated)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.DEBUG)
    test_reports = [
        "edgar/data/1000045/000095017022000940/index.json",
        "edgar/data/1358633/000173112220000705/index.json", # direct ins file
        "edgar/data/1000209/000095017022003603/index.json",
        "edgar/data/1000228/000100022822000016/index.json",
        "edgar/data/1000229/000095017022001087/index.json",
        "edgar/data/1000230/000143774922006521/index.json",
        "edgar/data/1000298/000155837022003437/index.json",
        "edgar/data/1000623/000100062322000016/index.json",
        "edgar/data/1000683/000121390022016788/index.json"
    ]

    print("https://www.sec.gov/Archives/edgar/data/1000045/000095017021004287/nick-20210930_pre.xml".replace("_pre.xml", "")[-8:])

    # adsh = None
    # report_index_json_url = test_reports[1]
    # SecFullIndexFilePostProcessor._find_xbrl_files((adsh, None, None, None, None, report_index_json_url))