from _00_common.DBManagement import DBManager
from _00_common.DebugUtils import DataAccessTool, TestSetCreatorTool

from testintegration.sub.SubMassTestingTools import read_sub_zip_content, read_sub_xml_content

from typing import List, Dict, Tuple

import pandas as pd


default_workdir = "d:/secprocessing"

dbmgr = DBManager(work_dir=default_workdir)
dataUtils = DataAccessTool(default_workdir)
testsetCreator = TestSetCreatorTool(default_workdir)

cols = ['adsh', 'cik', 'name', 'sic', 'fye', 'form', 'period', 'filed', 'accepted', 'fy', 'fp']
compare_cols = [x for x in cols if x is not "adsh"]


def read_quarter_data(year: int, qrtr: int) -> Tuple[pd.DataFrame, pd.DataFrame]:
    sub_zip_df = read_sub_zip_content(dbmgr, dataUtils, year, qrtr)[cols]
    sub_zip_df.rename(lambda x: x + "_zip", axis = 1, inplace=True)

    sub_xml_df = read_sub_xml_content(dbmgr, testsetCreator, year, qrtr)
    sub_xml_df.rename(lambda x: x + "_xml", axis = 1, inplace=True)

    return sub_zip_df, sub_xml_df


def merge(sub_zip_df: pd.DataFrame, sub_xml_df: pd.DataFrame) -> pd.DataFrame:
    return pd.merge(sub_zip_df, sub_xml_df, how = "outer", left_on=['adsh_zip'], right_on=['adsh_xml'])


def compare_adsh(merged_df: pd.DataFrame):
    adshs_not_in_zip = merged_df[merged_df.adsh_zip.isnull()].adsh_xml.to_list()
    adshs_not_in_xml = merged_df[merged_df.adsh_xml.isnull()].adsh_zip.to_list()

    print("not in zip: ", len(adshs_not_in_zip), adshs_not_in_zip)
    print("not in xml: ", len(adshs_not_in_xml), adshs_not_in_xml)


def compare_cols(merged_df: pd.DataFrame):
    same_adsh_df = merged_df[(~merged_df.adsh_zip.isnull()) & (~merged_df.adsh_xml.isnull())]

    compare_cols = [x for x in cols if x is not "adsh"]
    for comp_col in compare_cols:
        xml_col = comp_col + '_xml'
        zip_col = comp_col + '_zip'

        inequal_df = same_adsh_df[~(same_adsh_df[xml_col] == same_adsh_df[zip_col])][['adsh_xml', xml_col, zip_col]]
        inequal_adshs = inequal_df.adsh_xml.to_list()
        print(comp_col, len(inequal_adshs), inequal_adshs)


sub_zip_df, sub_xml_df = read_quarter_data(2021, 1)
merged_df = merge(sub_zip_df, sub_xml_df)
compare_adsh(merged_df=merged_df)
compare_cols(merged_df=merged_df)
#
# accepted format ist ganz anders, ausserdem stimmen die Minuten z.T. nicht
#
# es benötigt noch eine funktion, um das sub direkt ab tabelle berechnen können, so dass nicht alles immer wieder neu berechnet werden muss.
# variante wäre noch vergleichsspalten einzufügen, dann könnte man später einfacher per filter unterschiede suchen, oder auch prüfen, ob gewisse zeilen komplett anders sind

print(len(sub_zip_df))
print(len(sub_xml_df))
print(sub_xml_df.columns)