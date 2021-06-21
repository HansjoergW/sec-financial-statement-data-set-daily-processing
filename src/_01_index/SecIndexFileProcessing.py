from _00_common.DBManagement import DBManager
from _00_common.SecFileUtils import get_url_content
from _01_index.SecIndexFileParsing import SecIndexFileParser

import logging
import datetime
from typing import Dict
import json


class SecIndexFileProcessor:
    """
    - downloads the desired sec files, parses them and adds the information into the db.
    """
    index_json_url = "https://www.sec.gov/Archives/edgar/monthly/index.json"

    def __init__(self, dbmanager: DBManager, start_year:int, end_year: int, start_month: int = 1, end_month:int = 12, feed_dir: str = "./tmp/"):
        self.dbmanager = dbmanager
        self.start_year = start_year
        self.end_year = end_year
        self.start_month = start_month
        self.end_month = end_month
        self.feed_dir = feed_dir
        self.processdate = datetime.date.today().isoformat()

    def _parse_content_index_json(self) -> Dict[str, str]:
        dict: Dict[str, str] = {}
        json_content = get_url_content(self.index_json_url)

        json_data = json.loads(json_content)
        for item in json_data['directory']['item']:
            dict[item['name']] = item['last-modified']

        return dict

    def _month_year_iter(self):
        ym_from = 12 * self.start_year + self.start_month - 1
        ym_to = 12 * self.end_year + self.end_month
        for yearm in range(ym_from, ym_to):
            year, month = divmod(yearm, 12)
            yield year, month + 1

    def download_sec_feeds(self):
        json_content:Dict[str, str] = self._parse_content_index_json()

        for year, month in self._month_year_iter():
            logging.info("processing year: {} / month: {}".format(year, month))
            sec_file = SecIndexFileParser(year, month, feed_dir=self.feed_dir)

            filename = sec_file.feed_filename
            last_modified = json_content[filename]

            indexfiles_df = self.dbmanager.read_all_index_files()
            status_ser = indexfiles_df[indexfiles_df.sec_feed_file == filename].status

            # first time to process file
            if len(status_ser) == 0:
                logging.info("- first processing of {}".format(sec_file.feed_filename))
                self.dbmanager.insert_index_file(sec_file.feed_filename, self.processdate)
            else:
                status = status_ser.values[0]
                if status == last_modified:
                    logging.info("- already processed {} -> skip ".format(sec_file.feed_filename))
                    continue
                else:
                    logging.info("- continue {} ".format(sec_file.feed_filename))
                    self.dbmanager.update_index_file(sec_file.feed_filename, self.processdate)

            sec_file.download_sec_feed()
            df = sec_file.parse_sec_rss_feeds()
            existing_adshs = self.dbmanager.get_adsh_by_feed_file(sec_file.feed_filename)
            df = df[~df.index.isin(existing_adshs)]
            duplicated = sum(df.index.duplicated())
            logging.info("   duplicated: {}".format(duplicated))
            logging.info("   read entries: {}".format(len(df)))
            self.dbmanager.insert_feed_info(df)
            self.dbmanager.update_status_index_file(sec_file.feed_filename, last_modified)




