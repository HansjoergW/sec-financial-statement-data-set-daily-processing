from _00_common.DBManagement import DBManager
from _02_xml.SecFileManagement import SecIndexFile


class SecFilesProcessor:
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

    def _month_year_iter(self):
        ym_from = 12 * self.start_year + self.start_month - 1
        ym_to = 12 * self.end_year + self.end_month
        for yearm in range(ym_from, ym_to):
            year, month = divmod(yearm, 12)
            yield year, month + 1

    def download_sec_feeds(self):
        for year, month in self._month_year_iter():
            sec_file = SecIndexFile(year, month, feed_dir=self.feed_dir)
            sec_file.download_sec_feed()
            df = sec_file.parse_sec_rss_feeds()
            self.dbmanager.insert_feed_info(df)