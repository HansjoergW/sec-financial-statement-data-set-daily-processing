from _00_common.DBManagement import DBManager
from _01_index.SecIndexFileParsing import SecIndexFileParser

import logging
import datetime


class SecIndexFileProcessor:
    """
    - downloads the desired sec files, parses them and adds the information into the db.
    """

    def __init__(self, dbmanager: DBManager, start_year:int, end_year: int, start_month: int = 1, end_month:int = 12, feed_dir: str = "./tmp/"):
        self.dbmanager = dbmanager
        self.start_year = start_year
        self.end_year = end_year
        self.start_month = start_month
        self.end_month = end_month
        self.feed_dir = feed_dir
        self.processdate = datetime.date.today().isoformat()

    def _month_year_iter(self):
        ym_from = 12 * self.start_year + self.start_month - 1
        ym_to = 12 * self.end_year + self.end_month
        for yearm in range(ym_from, ym_to):
            year, month = divmod(yearm, 12)
            yield year, month + 1

    def download_sec_feeds(self):
        for year, month in self._month_year_iter():
            logging.info("processing year: {} / month: {}".format(year, month))
            sec_file = SecIndexFileParser(year, month, feed_dir=self.feed_dir)

            indexfiles_df = self.dbmanager.read_all_index_files()
            status_ser = indexfiles_df[indexfiles_df.sec_feed_file == sec_file.feed_filename].status

            # first time to process file
            if len(status_ser) == 0:
                logging.info("- first processing of {}".format(sec_file.feed_filename))
                self.dbmanager.insert_index_file(sec_file.feed_filename, self.processdate)
            else:
                status = status_ser.values[0]
                if status == 'done':
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


