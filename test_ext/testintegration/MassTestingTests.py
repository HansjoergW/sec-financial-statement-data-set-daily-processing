from _00_common.DebugUtils import DataAccessTool, TestSetCreatorTool
from _00_common.DBManagement import DBManager
from testintegration.MassTestingTools import read_mass_pre_xml_content, read_mass_pre_zip_content

import pytest

from typing import List, Dict, Tuple, Set, Union
from multiprocessing import Pool
import logging
import pandas as pd


""" Idee::
hier irgendwie die einzelnen Tests als Klassen ablegen.
zB. prüfen ob Anzahl Reports identisch, Total und pro Typ -> das erste, was wir sicherstellen möchten.

Die einzelnen TestAspekte müssen separiert werden, sonst gibt es ein durcheinander

"""

default_workdir = "d:/secprocessing"

dbmgr = DBManager(work_dir=default_workdir)
dataUtils = DataAccessTool(default_workdir)
testsetcreator = TestSetCreatorTool(default_workdir)

zip_data_df = read_mass_pre_zip_content(dbmgr, dataUtils, 2021, 1)
xml_data_df = read_mass_pre_xml_content(dbmgr)

adshs_in_zip = set(zip_data_df.adsh.unique().tolist())
adshs_in_xml = set(xml_data_df.adsh.unique().tolist())

adshs_in_both = adshs_in_xml.union(adshs_in_zip)
sorted_adshs_in_both = sorted(list(adshs_in_both))


def filter_for_adsh_and_statement(df: pd.DataFrame, adshs: List[str], stmt: str, inpth: int) -> pd.DataFrame:
    return df[df.adsh.isin(adshs) & (df.stmt == stmt) & (df.inpth == inpth)].copy()


# compare adshs in the data
def test_compare_adshs():
    not_in_xml = adshs_in_zip - adshs_in_xml
    not_in_zip = adshs_in_xml - adshs_in_zip

    print()
    print("Entries in XML: ", len(adshs_in_xml))
    print("Entries in ZIP: ", len(adshs_in_zip))
    print("not in xml: ", not_in_xml)
    print("not in zip: ", not_in_zip)
    print('-')
    print('number of reports per type: ')
    print('xml')
    print(xml_data_df.groupby(['stmt', 'inpth']).adsh.count())
    print('\nzip')
    print(zip_data_df.groupby(['stmt', 'inpth']).adsh.count())

    # we want to have all reports in the zip also present in the xml
    # however, we do not care if there additional entries present
    assert len(not_in_xml) == 0


def _compare_attribute(data: pd.Series):
    xml_tag_set = set(data.loc['tagList_xml'].split(','))
    zip_tag_set = set(data.loc['tagList_zip'].split(','))

    # test für exact, oder komplett in xml vorhanden unterscheiden -> bei apply müsste man dann mit expand arbeiten

    return len(zip_tag_set - xml_tag_set) == 0, len(xml_tag_set) == len(zip_tag_set)


def _compare_attributes(xml_df: pd.DataFrame, zip_df: pd.DataFrame) -> Tuple[int,int]:
    xml_idx = xml_df[['adsh', 'stmt', 'inpth', 'length','tagList']].set_index(['adsh', 'stmt', 'inpth'])
    zip_idx = zip_df[['adsh', 'stmt', 'inpth', 'length','tagList']].set_index(['adsh', 'stmt', 'inpth'])

    xml_idx.rename(columns = lambda x: x + '_xml', inplace=True)
    zip_idx.rename(columns = lambda x: x + '_zip', inplace=True)

    merged_df = pd.merge(xml_idx, zip_idx, left_index=True, right_index=True)
    merged_df[['tag_equals','tag_length_equals']] = merged_df.apply(_compare_attribute, axis = 1, result_type='expand')

    not_matching_df = merged_df[merged_df['tag_equals'] == False]
    not_exact_length_df = merged_df[merged_df['tag_length_equals'] == False]

    return len(not_matching_df), len(not_exact_length_df)


def _compare_reports(type: str, inpth: int, adshs_to_consider: List[str]) -> Dict[str, Union[str, int]]:
    xml_df = filter_for_adsh_and_statement(xml_data_df, adshs_to_consider, type, inpth)
    zip_df = filter_for_adsh_and_statement(zip_data_df, adshs_to_consider, type, inpth)

    xml_group_df = xml_df[['adsh', 'stmt', 'inpth','report']].groupby(['adsh', 'stmt', 'inpth']).count()
    zip_group_df = zip_df[['adsh', 'stmt', 'inpth','report']].groupby(['adsh', 'stmt', 'inpth']).count()

    xml_group_df.rename(columns = lambda x: x + '_xml', inplace=True)
    zip_group_df.rename(columns = lambda x: x + '_zip', inplace=True)

    merged_groupby = pd.merge(xml_group_df, zip_group_df, how="outer", left_index=True, right_index=True)
    merged_groupby['equal'] = merged_groupby['report_xml'] == merged_groupby['report_zip']
    merged_groupby_diff = merged_groupby[merged_groupby.equal == False]
    merged_groupby_diff.sort_index(inplace=True, level=['inpth'])

    xml_adshs_with = set(xml_df.adsh.unique().tolist())
    xml_adshs_without = set(adshs_to_consider) - xml_adshs_with

    zip_adshs_with = set(zip_df.adsh.unique().tolist())
    zip_adshs_without = set(adshs_to_consider) - zip_adshs_with

    missing_in_both = xml_adshs_without.intersection(zip_adshs_without)
    missing_in_xml = xml_adshs_without - zip_adshs_without
    missing_in_zip = zip_adshs_without - xml_adshs_without
    nr_unmatching_tags, nr_of_add_tags_in_xml = _compare_attributes(xml_df, zip_df)

    data_dict: Dict[str, Union[str, int]] = {
        "nr_adshs_with_in_xml" : len(xml_adshs_with),
        "nr_adshs_with_in_zip" : len(zip_adshs_with),
        # "nr_entries_in_xml"    : len(xml_df),
        # "nr_entries_in_zip"    : len(zip_df),

        "nr_adshs_without_in_xml": len(xml_adshs_without),
        "first_ten_adshs_without_in_xml": str(list(xml_adshs_without)[:10]),
        "nr_adshs_without_in_zip": len(zip_adshs_without),
        "first_ten_adshs_without_in_zip": str(list(zip_adshs_without)[:10]),

        "nr_missing_in_both" : len(missing_in_both),
        "first_ten_missing_in_both": str(list(missing_in_both)[:10]),

        "nr_missing_in_xml": len(missing_in_xml),
        "first_ten_missing_in_xml": str(list(missing_in_xml)[:10]),
        "nr_missing_in_zip": len(missing_in_zip),
        "first_ten_missing_in_zip": str(list(missing_in_zip)[:10]),

        "nr_unmatching_tags": nr_unmatching_tags,
        "nr_of_add_tags_in_xml": nr_of_add_tags_in_xml,

        "report_unequal_count": len(merged_groupby_diff),
        "nr_report_not_in_xml": len(merged_groupby_diff[merged_groupby_diff.report_xml.isna()]),
        "nr_report_not_in_zip": len(merged_groupby_diff[merged_groupby_diff.report_zip.isna()]),
        "first_ten_report_not_in_xml":  str(merged_groupby_diff[merged_groupby_diff.report_xml.isna()][:10]),
        "first_ten_report_not_in_zip":  str(merged_groupby_diff[merged_groupby_diff.report_zip.isna()][:10]),
    }

    return data_dict

def print_data_dict(stmt:str, inpth: int, data_dict: Dict[str, Union[str, int]]):
    print("\n----------------------------------------------------")
    print(f"{stmt} - {inpth}")
    print(f"ADSHs with entries in xml   : ", data_dict['nr_adshs_with_in_xml'])
    print(f"ADSHs with entries in zip   : ", data_dict['nr_adshs_with_in_zip'])
    # print(f"Entries in XML              : ", data_dict['nr_entries_in_xml'])
    # print(f"Entries in ZIP              : ", data_dict['nr_entries_in_zip'])
    print(f"Xml adshs without           : ", data_dict['nr_adshs_without_in_xml'], " - " , data_dict['first_ten_adshs_without_in_xml'])
    print(f"Zip adshs without           : ", data_dict['nr_adshs_without_in_zip'], " - " , data_dict['first_ten_adshs_without_in_zip'])

    print(f"Missing in both             : ", data_dict['nr_missing_in_both'],   ' - ', data_dict['first_ten_missing_in_both'])
    print(f"Only missing in xml         : ", data_dict['nr_missing_in_xml'], ' - ', data_dict['first_ten_missing_in_xml'])
    print(f"Only missing in zip         : ", data_dict['nr_missing_in_zip'], ' - ', data_dict['first_ten_missing_in_zip'])

    print(f"Entries with unmatching tags: (", data_dict['nr_unmatching_tags'], " / ", data_dict['nr_of_add_tags_in_xml'], ")")
    print("\n")
    print(f"Unequal counts:             : ", data_dict['report_unequal_count'])
    print(f"Reports not in xml          : ", data_dict['nr_report_not_in_xml'])
    print(f"Reports not in zip          : ", data_dict['nr_report_not_in_zip'])
    print(f"\nnot in xml (first 10)     : ", data_dict['first_ten_report_not_in_xml'])
    print(f"\nnot in zip (first 10)     : ", data_dict['first_ten_report_not_in_zip'])


def _compare_and_print(type: str, inpth: int, adshs_to_consider: List[str]):
    data = _compare_reports(type, inpth, adshs_to_consider)
    print_data_dict(type, inpth, data)


def test_compare_CP():
    adshs_to_consider = sorted_adshs_in_both # [:100]
    _compare_and_print('CP', 0, adshs_to_consider)

def test_compare_BS():
    adshs_to_consider = sorted_adshs_in_both # [:100]
    #adshs_to_consider = ["0000883984-21-000005"]
    _compare_and_print('BS', 0, adshs_to_consider)
    _compare_and_print('BS', 1, adshs_to_consider)


def test_compare_IS():
    adshs_to_consider = sorted_adshs_in_both # [:100]
    _compare_and_print('IS', 0, adshs_to_consider)
    _compare_and_print('IS', 1, adshs_to_consider)


def test_compare_CI():
    adshs_to_consider = sorted_adshs_in_both # [:100]
    _compare_and_print('CI', 0, adshs_to_consider)
    _compare_and_print('CI', 1, adshs_to_consider)


def test_compare_CF():
    adshs_to_consider = sorted_adshs_in_both # [:100]
    _compare_and_print('CF', 0, adshs_to_consider)
    _compare_and_print('CF', 1, adshs_to_consider)


def test_compare_EQ():
    adshs_to_consider = sorted_adshs_in_both # [:100]
    _compare_and_print('EQ', 0, adshs_to_consider)
    _compare_and_print('EQ', 1, adshs_to_consider)



# Tests
# 1. Adshs vergleichen
# 2. Anzahl Statements vergleichen
# 3. Statement typen vergleichen
# 4. Reihenfolge vergleichen (falls in der richtingen Reihenfolge geschrieben wurde)


if __name__ == '__main__':
    # test_preXmlParsing()
    pass