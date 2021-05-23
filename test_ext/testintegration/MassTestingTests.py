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
    print(xml_data_df.groupby('stmt').adsh.count())
    print('\nzip')
    print(zip_data_df.groupby('stmt').adsh.count())

    # we want to have all reports in the zip also present in the xml
    # however, we do not care if there additional entries present
    assert len(not_in_xml) == 0


def test_compare_CP():
    xml_cp_df = filter_for_adsh_and_statement(xml_data_df, sorted_adshs_in_both, 'CP')
    zip_cp_df = filter_for_adsh_and_statement(zip_data_df, sorted_adshs_in_both, 'CP')

    xml_adshs_with_cp = set(xml_cp_df.adsh.unique().tolist())
    xml_adshs_without_cp = adshs_in_xml - xml_adshs_with_cp

    print("")
    print("CP Entries in XML: ", len(xml_cp_df))
    print("CP Entries in ZIP: ", len(zip_cp_df))
    print("XML adshs without CP: ", xml_adshs_without_cp)


def test_compare_BS():
    adshs_to_consider = sorted_adshs_in_both[:100]
    xml_bs_df = filter_for_adsh_and_statement(xml_data_df, adshs_to_consider, 'BS')
    zip_bs_df = filter_for_adsh_and_statement(zip_data_df, adshs_to_consider, 'BS')

    xml_adshs_with_bs = set(xml_bs_df.adsh.unique().tolist())
    xml_adshs_without_bs = set(adshs_to_consider) - xml_adshs_with_bs

    print("")
    print("BS Entries in XML: ", len(xml_bs_df))
    print("BS Entries in ZIP: ", len(zip_bs_df))
    print("XML adshs without BS: ", len(xml_adshs_without_bs), " - " , xml_adshs_without_bs)



"""
Data:

                  

"""


# Tests
# 1. Adshs vergleichen
# 2. Anzahl Statements vergleichen
# 3. Statement typen vergleichen
# 4. Reihenfolge vergleichen (falls in der richtingen Reihenfolge geschrieben wurde)


if __name__ == '__main__':
    # test_preXmlParsing()
    pass