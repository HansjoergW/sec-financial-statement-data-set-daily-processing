from _00_common.DBManagement import DBManager
from _00_common.SecFileUtils import get_url_content


class SecIndexIndexJsonParser:
    index_json_url = "https://www.sec.gov/Archives/edgar/monthly/index.json"

    def __init__(self, dbmanager: DBManager):
        self.dbmanager = dbmanager


    def _parse_content(self):
        json_content = get_url_content(self.index_json_url)

        print(json_content)


if __name__ == '__main__':

    SecIndexIndexJsonParser(DBManager('.tmp'))._parse_content()