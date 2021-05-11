# compares if the content auf quarter-zip file is contained in the database and if the content is equal to the
# parsed csv content
# Checks that are done:
# 1. all 10-k and 10-q reports are of the zip files are available
# are the contents in the csv file the same
from src._00_common import DBManager
from src._00_common import DataAccessTool, ReparseTool

import pandas as pd
from typing import List, Set
import glob
import os

dbg_tools = DataAccessTool("d:/secprocessing/")
workdir_default = "d:/secprocessing/"

def filter_relevant_reports(sub_df: pd.DataFrame) -> pd.DataFrame:
    return sub_df[sub_df.form.isin(['10-K', '10-Q'])].copy()


def read_entries_from_sec_processing(dbm: DBManager, year: int, months: List[int]) -> pd.DataFrame:
    conn = dbm.get_connection()
    months = ','.join([str(month) for month in months])

    try:
        sql = '''SELECT * from sec_report_processing WHERE filingYear = {} and filingMonth in ({}) and preParseState like 'parsed%' and numParseState like 'parsed%' '''.format(year, months)
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

def compare_adsh_reports(adsh: str, zip_pre_df: pd.DataFrame, process_pre_data: pd.DataFrame):
    zip_report_count = zip_pre_df.groupby(['report', 'stmt']).adsh.count().to_frame()

    if len(process_pre_data) == 0:
        print(f"{adsh} - no data")
        return

    process_report_count = process_pre_data.groupby(['report', 'stmt']).adsh.count().to_frame()

    zip_report_count.rename(columns = lambda x: x + '_count_zip', inplace=True)
    process_report_count.rename(columns = lambda x: x + '_count_xml', inplace=True)

    if (len(zip_report_count) != len(process_report_count)):
        print('count diff', end = ' : ')

    df_merge = pd.merge(zip_report_count, process_report_count, how="outer", left_index=True, right_index=True)
    df_diff = df_merge[(df_merge.adsh_count_zip != df_merge.adsh_count_xml)]

    diff_len = len(df_diff)
    if diff_len > 0:
        print(f"{adsh} - {diff_len}")


def compare_pre_content_for_adsh(adsh: str, zip_pre_df: pd.DataFrame, process_pre_data: pd.DataFrame):
    compare_adsh_reports(adsh, zip_pre_df, process_pre_data)

    # geht so nicht, die report nummer muss berücksichtigt werden
    # zip_pre_df.set_index(['adsh', 'tag','version', 'stmt', 'line'], inplace=True)
    # process_pre_data.set_index(['adsh', 'tag','version', 'stmt', 'line'], inplace=True)
    #
    # zip_pre_df.rename(columns = lambda x: x + '_zip', inplace=True)
    # process_pre_data.rename(columns = lambda x: x + '_xml', inplace=True)
    #
    # df_merge = pd.merge(zip_pre_df, process_pre_data, how="outer", left_index=True, right_index=True)
    # df_diff = df_merge[(df_merge.negating_xml != df_merge.negating_zip)|(df_merge.inpth_xml != df_merge.inpth_zip)]
    # zip_len = len(zip_pre_df)
    # xml_len = len(process_pre_data)
    # diff = len(df_diff)
    # outstr = f"{adsh} - zip_len: {zip_len} - xml_len: {xml_len} - diff_len: {diff}"
    # print(outstr)


def compare_by_adsh_and_file(adsh: str, csvPreFile: str, zip_pre_adsh_df: pd.DataFrame, zip_num_df: pd.DataFrame):
    process_pre_adsh_data = pd.read_csv(csvPreFile, header=0, delimiter="\t")
    process_pre_adsh_data.drop(columns=['rfile'], inplace=True)

    compare_pre_content_for_adsh(adsh, zip_pre_adsh_df, process_pre_adsh_data)

    # process_num_data = pd.read_csv(process_table_adsh_df.csvNumFile.to_list()[0], header=0, delimiter="\t")
    # zip_num_adsh_data = zip_num_df[zip_num_df.adsh == adsh]
    # print("")


def compare_by_adsh(adsh: str, process_df: pd.DataFrame, zip_pre_df: pd.DataFrame, zip_num_df: pd.DataFrame, use_temp_folder: bool):
    if use_temp_folder:
        csvPreFile = f'D:/secprocessing/tmp/precsv/{adsh}_pre.csv'
    else:
        process_table_adsh_df = process_df[process_df.accessionNumber == adsh]
        csvPreFile = process_table_adsh_df.csvPreFile.to_list()[0]
    zip_pre_adsh_df = zip_pre_df[zip_pre_df.adsh == adsh].copy()
    compare_by_adsh_and_file(adsh, csvPreFile, zip_pre_adsh_df, zip_num_df)


def compare_adsh_contents(adshs_in_both: Set[str], process_df: pd.DataFrame, zip_pre_df: pd.DataFrame, zip_num_df: pd.DataFrame, use_temp_folder: bool):
    for adsh in list(adshs_in_both)[:100]:
        compare_by_adsh(adsh, process_df, zip_pre_df, zip_num_df, use_temp_folder)


def compare_all():
    quarterfile = dbg_tools._get_zipfilename(2021, 1)
    feed_year: int = 2021
    feed_months: List[int] = [1,2,3]

    dbm = dbg_tools.dbmgr

    zip_sub_df_all = dbg_tools._read_file_from_zip(quarterfile, "sub.txt")
    zip_sub_df = filter_relevant_reports(zip_sub_df_all)

    process_df = read_entries_from_sec_processing(dbm, feed_year, feed_months)

    zip_pre_df_all = dbg_tools._read_file_from_zip(quarterfile, "pre.txt")
    zip_pre_df_all.drop(columns=['rfile','plabel'], inplace=True)

    zip_num_df_all = dbg_tools._read_file_from_zip(quarterfile, "num.txt")


    adshs_in_both: Set[str] = compare_adsh_entries(zip_sub_df, process_df)
    # zip_pre_df_filtered = zip_pre_df_all[zip_pre_df_all.adsh.isin(adshs_in_both)]
    # zip_num_df_filtered = zip_num_df_all[zip_num_df_all.adsh.isin(adshs_in_both)]

    compare_adsh_contents(adshs_in_both, process_df, zip_pre_df_all, zip_num_df_all, True)

    #compare_by_adsh("'0001437749-21-005151'", process_df, zip_pre_df_all, zip_num_df_all)

def compare_from_test_dir():
    quarterfile = dbg_tools._get_zipfilename(2021, 1)
    pre_test_dir = 'd:/secprocessing/tmp/precsv/'
    files = glob.glob(pre_test_dir + "*.csv")
    files: List[str] = [os.path.basename(path) for path in files]
    adshs: Set[str] = set([x.split('_')[0] for x in files])

    dbm = dbg_tools.dbmgr

    zip_pre_df_all = dbg_tools._read_file_from_zip(quarterfile, "pre.txt")
    zip_pre_df_all = zip_pre_df_all[zip_pre_df_all.adsh.isin(adshs)].copy()
    zip_pre_df_all.drop(columns=['rfile','plabel'], inplace=True)

    compare_adsh_contents(adshs, None, zip_pre_df_all, None, True)

def reparse_pre(count: int):
    reparse = ReparseTool(workdir_default)
    reparse.reparse_pre(2021, [1,2,3], 'd:/secprocessing/tmp/precsv/', count)


def direct_test():
    # 0000883984-21-000005 - hat zusätzliche Einträge im XML in den Statements
    #    StatementScenarioAxis und ScenarioUnspecifiedDomain von srt/2020 erscheinen nicht, erst ab StatementLineItems..
    # 0001558370-21-002205
    #    CoverPage missing

    adsh = '0000004457-21-000019'
    preCsvFile = f'D:/secprocessing/tmp/precsv/{adsh}_pre.csv'
    #preCsvFile = 'd:/secprocessing/csv/2021-05-08/0000883984-21-000005_pre.csv'
    quarterfile = dbg_tools._get_zipfilename(2021, 1)
    zip_pre_df_all = dbg_tools._read_file_from_zip(quarterfile, "pre.txt")
    zip_pre_df_all.drop(columns=['rfile','plabel'], inplace=True)
    zip_pre_adsh_df = zip_pre_df_all[zip_pre_df_all.adsh == adsh].copy()
    compare_by_adsh_and_file(adsh, preCsvFile, zip_pre_adsh_df, None)

if __name__ == '__main__':
    #compare_all()
    #reparse_pre(100)
    #compare_from_test_dir()
    #reparse_pre(100)
    direct_test()
    pass




    # problem, die gruppierung muss beim vergleich beachtet
    # es wird so eine art universelle gruppe benötigt.. so was wie
    # statement-anz rows..
    # vlt. würde es auch helfen, wenn nur die relevanten statements gefiltert
    # (werden.)


    # man müsste evtl. schrittweise vorgehen, d.h., zuerst prüfen, ob die Anzahl Reports/Statements stimmen, und von daher
    # weitertesten. evtl. kann man so auch die reportnr richtigmachen.
    # mit den reports könnte man auch gleich die anzahl einträge testen.

