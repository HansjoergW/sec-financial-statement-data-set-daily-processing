from secdaily._00_common.DBManagement import DBManager
from secdaily._00_common.DebugUtils import DataAccessTool, TestSetCreatorTool

from testintegration.sub.SubMassTestingTools import read_sub_zip_content, read_sub_xml_content, read_and_parse_direct_from_table

from typing import List, Dict, Tuple

import pandas as pd


default_workdir = "d:/secprocessing"

dbmgr = DBManager(work_dir=default_workdir)
dataUtils = DataAccessTool(default_workdir)
testsetCreator = TestSetCreatorTool(default_workdir)

cols = ['adsh', 'cik', 'name', 'sic', 'fye', 'form', 'period', 'filed', 'accepted', 'fy', 'fp']


def read_quarter_data(year: int, qrtr: int) -> Tuple[pd.DataFrame, pd.DataFrame]:
    sub_zip_df = read_sub_zip_content(dbmgr, dataUtils, year, qrtr)[cols]
    sub_zip_df.rename(lambda x: x + "_zip", axis = 1, inplace=True)

    sub_xml_df = read_sub_xml_content(dbmgr, testsetCreator, year, qrtr)
    sub_xml_df.rename(lambda x: x + "_xml", axis = 1, inplace=True)

    return sub_zip_df, sub_xml_df


def read_quarter_data_direct_from_db(year: int, qrtr: int, adshs: List[str] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
    sub_zip_df = read_sub_zip_content(dbmgr, dataUtils, year, qrtr, adshs)[cols]

    sub_zip_df.rename(lambda x: x + "_zip", axis = 1, inplace=True)

    sub_xml_df = read_and_parse_direct_from_table(dbmgr, year, qrtr, adshs)
    sub_xml_df.rename(lambda x: x + "_xml", axis = 1, inplace=True)

    return sub_zip_df, sub_xml_df


def merge(sub_zip_df: pd.DataFrame, sub_xml_df: pd.DataFrame) -> pd.DataFrame:
    # ignore 0229 fiscal ending
    mask = sub_zip_df.fye_zip == '0229'
    sub_zip_df.loc[mask, 'fye_zip'] = '0228'

    mask = sub_xml_df.fye_xml == '0229'
    sub_xml_df.loc[mask, 'fye_xml'] = '0228'

    return pd.merge(sub_zip_df, sub_xml_df, how = "outer", left_on=['adsh_zip'], right_on=['adsh_xml'])


def compare_adsh(merged_df: pd.DataFrame):
    adshs_not_in_zip = merged_df[merged_df.adsh_zip.isnull()].adsh_xml.to_list()
    adshs_not_in_xml = merged_df[merged_df.adsh_xml.isnull()].adsh_zip.to_list()

    print("not in zip: ", len(adshs_not_in_zip), adshs_not_in_zip)
    print("not in xml: ", len(adshs_not_in_xml), adshs_not_in_xml)


def compare_cols(merged_df: pd.DataFrame) -> pd.DataFrame:
    same_adsh_df = merged_df[(~merged_df.adsh_zip.isnull()) & (~merged_df.adsh_xml.isnull())].copy()

    compare_cols = [x for x in cols if x is not "adsh"]
    for comp_col in compare_cols:
        xml_col = comp_col + '_xml'
        zip_col = comp_col + '_zip'
        comp_col_name = comp_col + '_comp'
        same_adsh_df[comp_col_name] = (same_adsh_df[xml_col] == same_adsh_df[zip_col])
        inequal_df = same_adsh_df[~same_adsh_df[comp_col_name]][['adsh_xml', xml_col, zip_col]]
        inequal_adshs = inequal_df.adsh_xml.to_list()
        print(comp_col, len(inequal_adshs), inequal_adshs)

    return same_adsh_df

def compare_processed_content(dfs: Tuple[pd.DataFrame, pd.DataFrame]):
    sub_zip_df = dfs[0]
    sub_xml_df = dfs[1]
    merged_df = merge(sub_zip_df, sub_xml_df)
    compare_adsh(merged_df=merged_df)
    comp_result_df = compare_cols(merged_df=merged_df)

    fy_result = comp_result_df[['adsh_zip','form_zip','fp_zip','fy_zip','fye_zip','period_zip','fp_xml','fy_xml','fye_xml','period_xml','fy_comp','fye_comp', 'fp_comp']]
    # fy_result[(fy_result.fy_comp==False) & (fy_result.fye_comp==True)]
    # fy_result[ (fy_result.fye_comp==True) &(fy_result.form_zip=='10-K')]
    print(len(sub_zip_df))
    print(len(sub_xml_df))
    #print(sub_xml_df.columns)


# compare_processed_content(read_quarter_data(2021, 1))

# adshs = ['0000909832-21-000003']
adshs = None
compare_processed_content(read_quarter_data_direct_from_db(2021, 1, adshs))

