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


def _compare_attributes(xml_df: pd.DataFrame, zip_df: pd.DataFrame) -> Tuple[List,List]:
    xml_idx = xml_df[['adsh', 'stmt', 'inpth', 'length','tagList']].set_index(['adsh', 'stmt', 'inpth'])
    zip_idx = zip_df[['adsh', 'stmt', 'inpth', 'length','tagList']].set_index(['adsh', 'stmt', 'inpth'])

    xml_idx.rename(columns = lambda x: x + '_xml', inplace=True)
    zip_idx.rename(columns = lambda x: x + '_zip', inplace=True)

    merged_df = pd.merge(xml_idx, zip_idx, left_index=True, right_index=True)
    merged_df[['tag_equals','tag_length_equals']] = merged_df.apply(_compare_attribute, axis = 1, result_type='expand')

    not_matching_df = merged_df[merged_df['tag_equals'] == False]
    not_exact_length_df = merged_df[merged_df['tag_length_equals'] == False]

    return not_matching_df.index.get_level_values('adsh').to_list(), not_exact_length_df.index.get_level_values('adsh').to_list()


def _compare_reports(type: str, inpth: int, adshs_to_consider: List[str]) -> Dict[str, Union[str, int]]:
    xml_df = filter_for_adsh_and_statement(xml_data_df, adshs_to_consider, type, inpth)
    zip_df = filter_for_adsh_and_statement(zip_data_df, adshs_to_consider, type, inpth)

    xml_group_df = xml_df[['adsh', 'stmt', 'inpth','report']].groupby(['adsh', 'stmt', 'inpth']).count()
    zip_group_df = zip_df[['adsh', 'stmt', 'inpth','report']].groupby(['adsh', 'stmt', 'inpth']).count()

    xml_group_df.rename(columns = lambda x: x + '_xml', inplace=True)
    zip_group_df.rename(columns = lambda x: x + '_zip', inplace=True)

    xml_adshs_with = set(xml_df.adsh.unique().tolist())
    xml_adshs_without = set(adshs_to_consider) - xml_adshs_with

    zip_adshs_with = set(zip_df.adsh.unique().tolist())
    zip_adshs_without = set(adshs_to_consider) - zip_adshs_with

    missing_in_both = xml_adshs_without.intersection(zip_adshs_without)
    missing_in_xml = xml_adshs_without - zip_adshs_without
    missing_in_zip = zip_adshs_without - xml_adshs_without

    not_matching_list, not_exact_length_list = _compare_attributes(xml_df, zip_df)

    data_dict: Dict[str, Union[str, int]] = {
        "nr_adshs_with_in_xml" : len(xml_adshs_with),
        "nr_adshs_with_in_zip" : len(zip_adshs_with),

        "adshs_without_in_xml": list(xml_adshs_without),
        "adshs_without_in_zip": list(zip_adshs_without),

        "report_unequal_count": len(missing_in_xml) + len(missing_in_zip),
        "missing_in_both": list(missing_in_both),
        "missing_in_xml": list(missing_in_xml),
        "missing_in_zip": list(missing_in_zip),

        "unmatching_tags": not_matching_list,
        "add_tags_in_xml": not_exact_length_list,
    }

    return data_dict


def print_data_dict(stmt:str, inpth: int, data_dict: Dict[str, Union[str, int]]):
    print("\n----------------------------------------------------")
    print(f"{stmt} - {inpth}")
    print("ADSHs with entries in xml   : ", data_dict['nr_adshs_with_in_xml'])
    print("ADSHs with entries in zip   : ", data_dict['nr_adshs_with_in_zip'])

    print("Xml adshs without           : ", len(data_dict['adshs_without_in_xml']), " - " , str(data_dict['adshs_without_in_xml'][:10]))
    print("Zip adshs without           : ", len(data_dict['adshs_without_in_zip']), " - " , str(data_dict['adshs_without_in_zip'][:10]))

    print("Unequal counts:             : ", data_dict['report_unequal_count'])
    print("Missing in both             : ", len(data_dict['missing_in_both']), ' - ', str(data_dict['missing_in_both'][:10]))
    print("Only missing in xml         : ", len(data_dict['missing_in_xml']),  ' - ', str(data_dict['missing_in_xml'][:10]))
    print("Only missing in zip         : ", len(data_dict['missing_in_zip']),  ' - ', str(data_dict['missing_in_zip'][:10]))
    print("Unmatching Tags             : ", len(data_dict['unmatching_tags']),  ' - ', str(data_dict['unmatching_tags'][:10]))
    print("Additional Tags             : ", len(data_dict['add_tags_in_xml']),  ' - ', str(data_dict['add_tags_in_xml'][:10]))


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