# compares if the content auf quarter-zip file is contained in the database and if the content is equal to the
# parsed csv content
# Checks that are done:
# 1. all 10-k and 10-q reports are of the zip files are available
# are the contents in the csv file the same
from _00_common.DBManagement import DBManager
from _00_common.DebugUtils import DataAccessTool, ReparseTool

import pandas as pd
from typing import List, Set, Dict
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


def find_report_candidates_in_pre_data(zip_stmt: str, zip_tag_version_set: Set[str], pre_reports_dict: Dict[str, List[Dict]]) -> List[int]:
    pre_same_statements = pre_reports_dict.get(zip_stmt, [])

    pre_report_candidates: List[int] = []
    for pre_same_statement in pre_same_statements:
        pre_report = pre_same_statement['report']
        pre_tag_version_set = pre_same_statement['tagset']

        if len(zip_tag_version_set - pre_tag_version_set) == 0:
            pre_report_candidates.append(pre_report)

    return pre_report_candidates


def compare_adsh_reports(adsh: str, zip_pre_df: pd.DataFrame, process_pre_data: pd.DataFrame, case_dict: List[Dict[str,str]]):

    if len(process_pre_data) == 0:
        #print(f"{adsh} - no data")
        case_dict.append({'no data':''})
        return

    # Daten von process_pre_data aufbereiten
    # - wird verwendet um den passenden report zu finden
    # dict mit stmt -> darin liste mit dictt mit reports für dieses statement
    # stmt dict enthält
    #  - report nummer
    #  - stmt
    #  - liste mit tag_version

    pre_reports_dict: Dict[str, List[Dict]] = {}
    pre_reports = process_pre_data.report.unique()
    for pre_report in pre_reports:
        pre_report_entries = process_pre_data[process_pre_data.report == pre_report]
        stmt = pre_report_entries.stmt.to_list()[0]
        tag_version_set = set((pre_report_entries.tag + "#" + pre_report_entries.version).to_list())
        report_dict: Dict = {}
        report_dict['report'] = pre_report
        report_dict['stmt'] = stmt
        report_dict['tagset'] = tag_version_set

        if pre_reports_dict.get(stmt) == None:
            pre_reports_dict[stmt] = []

        pre_reports_dict.get(stmt).append(report_dict)


    zip_reports = zip_pre_df.report.unique()
    for zip_report in zip_reports:
        zip_report_entries = zip_pre_df[zip_pre_df.report == zip_report]
        stmt = zip_report_entries.stmt.to_list()[0]
        zip_tag_version_set = set((zip_report_entries.tag + "#" + zip_report_entries.version).to_list())

        if pre_reports_dict.get(stmt) is None:
            case_dict.append({stmt: 'not present'})
            continue

        pre_report_candidates = find_report_candidates_in_pre_data(stmt, zip_tag_version_set, pre_reports_dict)

        if len(pre_report_candidates) != 1:
           case_dict.append({stmt: 'possible canditates: ' + str(len(pre_report_candidates))})


    # zip_report_count = zip_pre_df.groupby(['report', 'stmt']).adsh.count().to_frame()
    # process_report_count = process_pre_data.groupby(['report', 'stmt']).adsh.count().to_frame()
    #
    # zip_report_count.rename(columns = lambda x: x + '_count_zip', inplace=True)
    # process_report_count.rename(columns = lambda x: x + '_count_xml', inplace=True)
    #
    # if (len(zip_report_count) != len(process_report_count)):
    #     print('count diff', end = ' : ')
    #
    # df_merge = pd.merge(zip_report_count, process_report_count, how="outer", left_index=True, right_index=True)
    # df_diff = df_merge[(df_merge.adsh_count_zip != df_merge.adsh_count_xml)]
    #
    # diff_len = len(df_diff)
    # if diff_len > 0:
    #     print(f"{adsh} - {diff_len}")


def compare_pre_content_for_adsh(adsh: str, zip_pre_df: pd.DataFrame, process_pre_data: pd.DataFrame, case_dict: List[Dict[str,str]]):
    compare_adsh_reports(adsh, zip_pre_df, process_pre_data, case_dict)

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


def compare_by_adsh_and_file(adsh: str, csvPreFile: str, zip_pre_adsh_df: pd.DataFrame, zip_num_df: pd.DataFrame, case_dict: List[Dict[str,str]]):
    process_pre_adsh_data = pd.read_csv(csvPreFile, header=0, delimiter="\t")
    process_pre_adsh_data.drop(columns=['rfile'], inplace=True)

    compare_pre_content_for_adsh(adsh, zip_pre_adsh_df, process_pre_adsh_data, case_dict)

    # process_num_data = pd.read_csv(process_table_adsh_df.csvNumFile.to_list()[0], header=0, delimiter="\t")
    # zip_num_adsh_data = zip_num_df[zip_num_df.adsh == adsh]
    # print("")


def compare_by_adsh(adsh: str, process_df: pd.DataFrame, zip_pre_df: pd.DataFrame, zip_num_df: pd.DataFrame, use_temp_folder: bool, case_dict: List[Dict[str,str]]):
    if use_temp_folder:
        csvPreFile = f'D:/secprocessing/tmp/precsv/{adsh}_pre.csv'
    else:
        process_table_adsh_df = process_df[process_df.accessionNumber == adsh]
        csvPreFile = process_table_adsh_df.csvPreFile.to_list()[0]
    zip_pre_adsh_df = zip_pre_df[zip_pre_df.adsh == adsh].copy()
    compare_by_adsh_and_file(adsh, csvPreFile, zip_pre_adsh_df, zip_num_df, case_dict)


def compare_adsh_contents(adshs_in_both: Set[str], process_df: pd.DataFrame, zip_pre_df: pd.DataFrame, zip_num_df: pd.DataFrame, use_temp_folder: bool):
    case_dicts: Dict[str, List[Dict[str,str]]] = {}
    for adsh in list(adshs_in_both)[:100]:
        case_dict: List[Dict[str,str]] = []
        compare_by_adsh(adsh, process_df, zip_pre_df, zip_num_df, use_temp_folder, case_dict)
        if len(case_dict) > 0:
            case_dicts[adsh] = case_dict

    print("total cases: " + str(len(case_dicts)))
    for k, v in case_dicts.items():
        print(k)
        for el in v:
            print("\t", el)


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


def compare_from_test_dir(exceptions: Set[str]):
    quarterfile = dbg_tools._get_zipfilename(2021, 1)
    pre_test_dir = 'd:/secprocessing/tmp/precsv/'

    files = glob.glob(pre_test_dir + "*.csv")
    files: List[str] = [os.path.basename(path) for path in files]
    adshs: Set[str] = set([x.split('_')[0] for x in files])

    # sonderfälle ausklammern, die noch nicht richtig geparsed werden
    adshs = adshs - exceptions


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

    adsh = '0000016918-21-000010' # IS is missing
    reparse = ReparseTool(workdir_default)
    reparse.reparse_pre_by_adshs([adsh], 'd:/secprocessing/tmp/precsv/')

    preCsvFile = f'D:/secprocessing/tmp/precsv/{adsh}_pre.csv'
    quarterfile = dbg_tools._get_zipfilename(2021, 1)
    zip_pre_df_all = dbg_tools._read_file_from_zip(quarterfile, "pre.txt")
    zip_pre_df_all.drop(columns=['rfile','plabel'], inplace=True)
    zip_pre_adsh_df = zip_pre_df_all[zip_pre_df_all.adsh == adsh].copy()
    case_dict: List[Dict[str,str]] = []
    compare_by_adsh_and_file(adsh, preCsvFile, zip_pre_adsh_df, None, case_dict)
    for el in case_dict:
        print("\t", el)


if __name__ == '__main__':
    #compare_all()
    #reparse_pre(100)
    #compare_from_test_dir(set(['0000018255-21-000004']))
    #reparse_pre(100)
    direct_test()
    pass

"""
History:
- find all reports
12.05.2021       - 46
13.05.2021-07:00 - 42
13.05.2021-12:11 - 30 -> loc labels können auch '.' enthalten -> Trenner für key und plabel von . auf $$$ gesetzt
13.05.2021-12:24 - 26 -> "stmt" keys auf to lowercase vergleichen
13.05.2021-12.46 - 

"""


    # problem, die gruppierung muss beim vergleich beachtet
    # es wird so eine art universelle gruppe benötigt.. so was wie
    # statement-anz rows..
    # vlt. würde es auch helfen, wenn nur die relevanten statements gefiltert
    # (werden.)


    # man müsste evtl. schrittweise vorgehen, d.h., zuerst prüfen, ob die Anzahl Reports/Statements stimmen, und von daher
    # weitertesten. evtl. kann man so auch die reportnr richtigmachen.
    # mit den reports könnte man auch gleich die anzahl einträge testen.

"""
Probleme:
1. es gibt im selben Report oft auch "doppelte" Gruppen mit gleichen Einträgen
2. Anzahl Gruppen ist nicht immer gleich 
3. Die report Nummern sind oft nicht in der gleichen Reihenfolge
4. Es gibt oft mehrere Reports pro Kategorie
5. Die Anzahl  Zeilen in den Gruppen ist nicht immer gleich 
6. Dasselbe Tag kann mehrmals vorkommen, aber mit anderm label..

Was ist das Ziel:
-> alles was in zip ist, ist auch in geparstem XMl, mehr sollte ok sein
-> Ziel müsste sein, den Inhalt aus der Zip Datei im XML wiederzufinden, und zwar komplett
-> wenn wir also eine Gruppe mit dem selben Statement finden, dann müsste geprüft werden, ob alle diese Einträge 
   vorhandne sind.
-> wir iter
-> wir akzeptieren mehr Reports und mehr zeilen, aber keine fehlenden
-> die Reihenfolge muss auch geprüft werden.
d.h.
Loop über die report Nr aus dem Zip
-> suche in den XML Daten mit Reports, welche die gleichen Tags und Versionen beinhalten
-> prüfen auf die selben Werte
-> prüfen auf die selbe Reihenfolge

"""