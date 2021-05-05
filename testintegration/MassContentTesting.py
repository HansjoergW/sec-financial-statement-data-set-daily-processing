# compares if the content auf quarter-zip file is contained in the database and if the content is equal to the
# parsed csv content
# Checks that are done:
# 1. all 10-k and 10-q reports are of the zip files are available
# are the contents in the csv file the same
from _00_common.DBManagement import DBManager
import zipfile
import pandas as pd
from typing import List


def read_file_from_zip(zipfile_to_read: str, file_to_read: str) -> pd.DataFrame:
    with zipfile.ZipFile(zipfile_to_read, "r") as myzip:
        return pd.read_csv(myzip.open(file_to_read), header=0, delimiter="\t")


def filter_relevant_reports(sub_df: pd.DataFrame) -> pd.DataFrame:
    return sub_df[sub_df.form.isin(['10-K', '10-Q'])].copy()


def read_entries_from_sec_feeds(dbm: DBManager, files: List[str]) -> pd.DataFrame:
    conn = dbm._get_connection()
    files_list = ','.join(["'" + file + "'" for file in files])

    try:
        sql = '''SELECT * from sec_feeds WHERE sec_feed_file in ({}) and status = 'copied' '''.format(files_list)
        return pd.read_sql_query(sql, conn)
    finally:
        conn.close()


def compare_adsh(zip_df: pd.DataFrame, xml_df: pd.DataFrame):
    zip_adshs = zip_df.adsh.tolist()
    xml_adshs = xml_df.accessionNumber.tolist()

    zip_adshs_set = set(zip_adshs)
    xml_adshs_set = set(xml_adshs)

    print("in zip, but not in xml: ", zip_adshs_set - xml_adshs_set)
    print("in xml, but not in zip: ", xml_adshs_set - zip_adshs_set)


if __name__ == '__main__':
    workdir_default = "d:/secprocessing/"
    quarterfile = "d:/secprocessing/quarterzip/2021q1.zip"
    feed_files = ["xbrlrss-2021-01.xml","xbrlrss-2021-02.xml","xbrlrss-2021-03.xml"]

    dbm = DBManager(workdir_default)

    zip_sub_df_all = read_file_from_zip(quarterfile, "sub.txt")
    zip_sub_df = filter_relevant_reports(zip_sub_df_all)
    print(zip_sub_df.shape)

    xml_sub_df = read_entries_from_sec_feeds(dbm, feed_files)
    print(xml_sub_df.shape)

    compare_adsh(zip_sub_df, xml_sub_df)




    special_df = zip_sub_df[zip_sub_df.adsh == '0001437749-21-004277']
    print(special_df.shape)

# Notiz: 0001437749-21-004277 ist doppelt vorhanden, sowohl im Februar, wie im März, mit den exakt gleichen Daten
# - besser auf filling month und jahr einschränken -> filing data noch splitten...