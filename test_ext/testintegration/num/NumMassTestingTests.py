from _00_common.DebugUtils import DataAccessTool, TestSetCreatorTool
from _00_common.DBManagement import DBManager

from testintegration.num.NumMassTestingTools import read_mass_num_zip_content, read_mass_num_xml_content

from typing import List, Dict, Tuple, Set, Union
import pandas as pd

default_workdir = "d:/secprocessing"
merged_tmp_file = default_workdir + "/tmp/nummerge.csv"

def filter_for_adsh(df: pd.DataFrame, adshs: List[str]) -> pd.DataFrame:
    return df[df.adsh.isin(adshs)].copy()

dataUtils = DataAccessTool(default_workdir)


def load_data():
    zip_data_df = read_mass_num_zip_content(dataUtils, 2021, 1)
    xml_data_df = read_mass_num_xml_content()

    adshs_in_zip = set(zip_data_df.adsh.unique().tolist())
    adshs_in_xml = set(xml_data_df.adsh.unique().tolist())

    adshs_in_both = adshs_in_xml.union(adshs_in_zip)
    sorted_adshs_in_both = sorted(list(adshs_in_both))

    # zip_data_matching_adshs_df = filter_for_adsh(zip_data_df, ['0000002178-21-000034'])
    # xml_data_matching_adshs_df = filter_for_adsh(xml_data_df, ['0000002178-21-000034'])
    zip_data_matching_adshs_df = filter_for_adsh(zip_data_df, sorted_adshs_in_both)
    xml_data_matching_adshs_df = filter_for_adsh(xml_data_df, sorted_adshs_in_both)

    return adshs_in_xml, adshs_in_zip, xml_data_matching_adshs_df, zip_data_matching_adshs_df


def test_save_uom_data():
    adshs_in_xml, adshs_in_zip, xml_data_matching_adshs_df, zip_data_matching_adshs_df = load_data()

    zip_data_matching_adshs_df.loc[zip_data_matching_adshs_df.coreg.isnull(), 'coreg'] = ""
    xml_data_matching_adshs_df.loc[xml_data_matching_adshs_df.coreg.isnull(), 'coreg'] = ""

    zip_data_matching_adshs_df['uom'] = zip_data_matching_adshs_df.uom.str.upper()
    xml_data_matching_adshs_df['uom'] = xml_data_matching_adshs_df.uom.str.upper()

    zip_idx = zip_data_matching_adshs_df.set_index(['adsh','tag','version','ddate', 'qtrs', 'coreg'])[['uom']]
    xml_idx = xml_data_matching_adshs_df.set_index(['adsh','tag','version','ddate', 'qtrs', 'coreg'])[['uom']]

    zip_idx.rename(columns = lambda x: x + '_zip', inplace=True)
    xml_idx.rename(columns = lambda x: x + '_xml', inplace=True)

    #dauert ewigs
    merged_uom_df = pd.merge(xml_idx, zip_idx, how="outer", left_index=True, right_index=True)

    merged_uom_df.reset_index(inplace=True)
    uom_cols_df = merged_uom_df[['uom_zip','uom_xml']]

    uom_cols_grp_count_df = uom_cols_df.groupby(['uom_zip','uom_xml']).count()

    print("")





def test_save_merged_df():
    adshs_in_xml, adshs_in_zip, xml_data_matching_adshs_df, zip_data_matching_adshs_df = load_data()

    zip_data_matching_adshs_df.loc[zip_data_matching_adshs_df.coreg.isnull(), 'coreg'] = ""
    xml_data_matching_adshs_df.loc[xml_data_matching_adshs_df.coreg.isnull(), 'coreg'] = ""

    zip_data_matching_adshs_df['uom'] = zip_data_matching_adshs_df.uom.str.upper()
    xml_data_matching_adshs_df['uom'] = xml_data_matching_adshs_df.uom.str.upper()

    zip_idx = zip_data_matching_adshs_df.set_index(['adsh','tag','version','ddate', 'qtrs', 'coreg', 'uom'])[['value']]
    xml_idx = xml_data_matching_adshs_df.set_index(['adsh','tag','version','ddate', 'qtrs', 'coreg', 'uom'])[['value']]

    zip_idx.rename(columns = lambda x: x + '_zip', inplace=True)
    xml_idx.rename(columns = lambda x: x + '_xml', inplace=True)

    merged_pure_df = pd.merge(xml_idx, zip_idx, how="outer", left_index=True, right_index=True)

    merged_pure_df.to_csv(merged_tmp_file)


def test_compare_adshs():
    adshs_in_xml, adshs_in_zip, xml_data_matching_adshs_df, zip_data_matching_adshs_df = load_data()
    not_in_xml = adshs_in_zip - adshs_in_xml
    not_in_zip = adshs_in_xml - adshs_in_zip

    print()
    print("Entries in XML: ", len(adshs_in_xml))
    print("Entries in ZIP: ", len(adshs_in_zip))
    print("Not in xml    : ", not_in_xml)
    print("Not in zip    : ", not_in_zip)

    entries_total_xml = len(xml_data_matching_adshs_df)
    entries_total_zip = len(zip_data_matching_adshs_df)

    print("Entries total in XML: ", entries_total_xml)
    print("Entries total in ZIP: ", entries_total_zip)
    print("Entries diff        : ", abs(entries_total_xml - entries_total_zip))

    # we want to have all reports in the zip also present in the xml
    # however, we do not care if there additional entries present
    assert len(not_in_xml) == 0


def test_compare_content():

    ### Don't forget to recreate file!!!!

    merged_pure_df = pd.read_csv(merged_tmp_file)
    # merged_pure_df = merged_pure_df[merged_pure_df.adsh.isin(['0000002178-21-000034'])]
    merged_pure_df.set_index(['adsh','tag','version','ddate', 'qtrs', 'coreg', 'uom'], inplace=True)

    # filtern von value spalten mit null
    merged_df = merged_pure_df[~(merged_pure_df.value_xml.isnull() & merged_pure_df.value_zip.isnull())]
    duplicated = merged_df[merged_df.index.duplicated(keep=False)]
    print()
    print("Check Duplicated Index Count: ", len(duplicated))
    print("Entries total pure merge: ", len(merged_pure_df))

    merged_df['is_equal'] = (merged_df.value_zip == merged_df.value_xml)

    equal_df = merged_df[merged_df.is_equal == True]
    not_equal_df = merged_df[merged_df.is_equal == False]

    print("Entries total in merged : ", len(merged_df))
    print("Entries equal           : ", len(equal_df))
    print("Entries not equal       : ", len(not_equal_df))


