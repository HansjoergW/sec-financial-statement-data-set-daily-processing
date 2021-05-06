# compares if the content auf quarter-zip file is contained in the database and if the content is equal to the
# parsed csv content
# Checks that are done:
# 1. all 10-k and 10-q reports are of the zip files are available
# are the contents in the csv file the same
from _00_common.DBManagement import DBManager
import zipfile
import pandas as pd
from typing import List, Set


def read_file_from_zip(zipfile_to_read: str, file_to_read: str) -> pd.DataFrame:
    with zipfile.ZipFile(zipfile_to_read, "r") as myzip:
        return pd.read_csv(myzip.open(file_to_read), header=0, delimiter="\t")


def filter_relevant_reports(sub_df: pd.DataFrame) -> pd.DataFrame:
    return sub_df[sub_df.form.isin(['10-K', '10-Q'])].copy()


def read_entries_from_sec_processing(dbm: DBManager, year: int, months: List[int]) -> pd.DataFrame:
    conn = dbm._get_connection()
    months = ','.join([str(month) for month in months])

    try:
        sql = '''SELECT * from sec_report_processing WHERE filingYear = {} and filingMonth in ({}) and preParseState = 'parsed' and numParseState = 'parsed' '''.format(year, months)
        return pd.read_sql_query(sql, conn)
    finally:
        conn.close()


def compare_adsh_entries(zip_df: pd.DataFrame, process_df: pd.DataFrame) -> Set[str]:
    zip_adshs = zip_df.adsh.tolist()
    process_adshs = process_df.accessionNumber.tolist()

    zip_adshs_set = set(zip_adshs)
    process_adshs_set = set(process_adshs)

    print("in zip, but not in xml: ", zip_adshs_set - process_adshs_set)
    print("in xml, but not in zip: ", process_adshs_set - zip_adshs_set)

    return zip_adshs_set.intersection(process_adshs_set)


def compare_pre_content_for_adsh(zip_pre_df: pd.DataFrame, xml_pre_df: pd.DataFrame):
    pass


def compare_adsh_contents(adshs_in_both: Set[str], process_df: pd.DataFrame, zip_pre_df: pd.DataFrame, zip_num_df: pd.DataFrame):

    for adsh in adshs_in_both:
        process_adsh_data_df = process_df[process_df.accessionNumber == adsh]
        #process_pre_data = pd.read_csv(process_adsh_data_df.csvPreFile.to_list()[0], header=0, delimiter="\t")
        
        
        zip_pre_adsh_data = zip_pre_df[zip_pre_df.adsh == adsh]
        zip_num_adsh_data = zip_num_df[zip_num_df.adsh == adsh]
        print("")




if __name__ == '__main__':
    workdir_default = "d:/secprocessing/"
    quarterfile = "d:/secprocessing/quarterzip/2021q1.zip"
    feed_year: int = 2021
    feed_months: List[int] = [1,2,3]

    dbm = DBManager(workdir_default)

    zip_sub_df_all = read_file_from_zip(quarterfile, "sub.txt")
    zip_sub_df = filter_relevant_reports(zip_sub_df_all)

    process_df = read_entries_from_sec_processing(dbm, feed_year, feed_months)

    adshs_in_both: Set[str] = compare_adsh_entries(zip_sub_df, process_df)

    zip_pre_df_all = read_file_from_zip(quarterfile, "pre.txt")
    zip_num_df_all = read_file_from_zip(quarterfile, "num.txt")

    # zip_pre_df_filtered = zip_pre_df_all[zip_pre_df_all.adsh.isin(adshs_in_both)]
    # zip_num_df_filtered = zip_num_df_all[zip_num_df_all.adsh.isin(adshs_in_both)]

    compare_adsh_contents(adshs_in_both, process_df, zip_pre_df_all, zip_num_df_all)

