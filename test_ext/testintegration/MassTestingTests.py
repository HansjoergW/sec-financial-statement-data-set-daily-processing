from _00_common.DebugUtils import DataAccessTool, TestSetCreatorTool
from _00_common.DBManagement import DBManager
from testintegration.MassTestingTools import read_mass_pre_xml_content, read_mass_pre_zip_content

import pytest

from typing import List, Dict, Tuple, Set
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


def filter_for_adsh_and_statement(df: pd.DataFrame, adshs: List[str], stmt: str) -> pd.DataFrame:
    return df[df.adsh.isin(adshs) & (df.stmt == stmt)].copy()


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


def _compare_reports(type: str, adshs_to_consider: List[str]):
    xml_bs_df = filter_for_adsh_and_statement(xml_data_df, adshs_to_consider, type)
    zip_bs_df = filter_for_adsh_and_statement(zip_data_df, adshs_to_consider, type)

    xml_bs_group_df = xml_bs_df[['adsh', 'stmt', 'inpth','report']].groupby(['adsh', 'stmt', 'inpth']).count()
    zip_bs_group_df = zip_bs_df[['adsh', 'stmt', 'inpth','report']].groupby(['adsh', 'stmt', 'inpth']).count()

    xml_bs_group_df.rename(columns = lambda x: x + '_xml', inplace=True)
    zip_bs_group_df.rename(columns = lambda x: x + '_zip', inplace=True)

    merged_groupby = pd.merge(xml_bs_group_df, zip_bs_group_df, how="outer", left_index=True, right_index=True)
    merged_groupby['equal'] = merged_groupby['report_xml'] == merged_groupby['report_zip']
    merged_groupby_diff = merged_groupby[merged_groupby.equal == False]
    merged_groupby_diff.sort_index(inplace=True, level=['inpth'])

    xml_adshs_with_bs = set(xml_bs_df.adsh.unique().tolist())
    xml_adshs_without_bs = set(adshs_to_consider) - xml_adshs_with_bs

    zip_adshs_with_bs = set(zip_bs_df.adsh.unique().tolist())
    zip_adshs_without_bs = set(adshs_to_consider) - zip_adshs_with_bs

    print("")
    print(f"ADSH with {type} Entries in XML: ", len(xml_adshs_with_bs))
    print(f"ADSH with {type} Entries in ZIP: ", len(zip_adshs_with_bs))
    print(f"{type} Entries in XML       : ", len(xml_bs_df))
    print(f"{type} Entries in ZIP       : ", len(zip_bs_df))
    print(f"XML adshs without {type}    : ", len(xml_adshs_without_bs), " - " , xml_adshs_without_bs)
    print(f"ZIP adshs without {type}    : ", len(zip_adshs_without_bs), " - " , zip_adshs_without_bs)
    missing_in_both = xml_adshs_without_bs.intersection(zip_adshs_without_bs)
    missing_in_xml = xml_adshs_without_bs - zip_adshs_without_bs
    missing_in_zip = zip_adshs_without_bs - xml_adshs_without_bs
    print(f"missing in both         : ", len(missing_in_both), ' - ', missing_in_both)
    print(f"only missing in xml     : ", len(missing_in_xml), ' - ',  missing_in_xml)
    print(f"only missing in zip     : ", len(missing_in_zip), ' - ',  missing_in_zip)
    print(f"\nentries with unmatching tags: ", _compare_attributes(xml_bs_df, zip_bs_df))

    print(f"\nunequal counts:         : ", len(merged_groupby_diff))
    print(f"{type} reports not in xml   : ", len(merged_groupby_diff[merged_groupby_diff.report_xml.isna()]))
    print(f"{type} reports not in zip   : ", len(merged_groupby_diff[merged_groupby_diff.report_zip.isna()]))
    print(f"\n{type} not in xml (first 10): ", merged_groupby_diff[merged_groupby_diff.report_xml.isna()][:10])
    print(f"\n{type} not in zip (first 10): ", merged_groupby_diff[merged_groupby_diff.report_zip.isna()][:10])


def test_compare_CP():
    adshs_to_consider = sorted_adshs_in_both # [:100]
    _compare_reports('CP', adshs_to_consider)


def test_compare_BS():
    adshs_to_consider = sorted_adshs_in_both # [:100]
    #adshs_to_consider = ["0000883984-21-000005"]
    _compare_reports('BS', adshs_to_consider)


def test_compare_IS():
    adshs_to_consider = sorted_adshs_in_both # [:100]
    _compare_reports('IS', adshs_to_consider)


def test_compare_CI():
    adshs_to_consider = sorted_adshs_in_both # [:100]
    _compare_reports('CI', adshs_to_consider)


def test_compare_CF():
    adshs_to_consider = sorted_adshs_in_both # [:100]
    _compare_reports('CF', adshs_to_consider)


def test_compare_EQ():
    adshs_to_consider = sorted_adshs_in_both # [:100]
    _compare_reports('EQ', adshs_to_consider)


def test_compare_UN():
    adshs_to_consider = sorted_adshs_in_both # [:100]
    _compare_reports('UN', adshs_to_consider)


"""

"""


# Tests
# 1. Adshs vergleichen
# 2. Anzahl Statements vergleichen
# 3. Statement typen vergleichen
# 4. Reihenfolge vergleichen (falls in der richtingen Reihenfolge geschrieben wurde)


if __name__ == '__main__':
    # test_preXmlParsing()
    pass