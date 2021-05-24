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
    adshs_to_consider = sorted_adshs_in_both # [:100]
    xml_bs_df = filter_for_adsh_and_statement(xml_data_df, adshs_to_consider, 'BS')
    zip_bs_df = filter_for_adsh_and_statement(zip_data_df, adshs_to_consider, 'BS')

    xml_adshs_with_bs = set(xml_bs_df.adsh.unique().tolist())
    xml_adshs_without_bs = set(adshs_to_consider) - xml_adshs_with_bs

    zip_adshs_with_bs = set(zip_bs_df.adsh.unique().tolist())
    zip_adshs_without_bs = set(adshs_to_consider) - zip_adshs_with_bs

    print("")
    print("ADSH with BS Entries in XML: ", len(xml_adshs_with_bs))
    print("ADSH with BS Entries in ZIP: ", len(zip_adshs_with_bs))
    print("BS Entries in XML: ", len(xml_bs_df))
    print("BS Entries in ZIP: ", len(zip_bs_df))
    print("XML adshs without BS: ", len(xml_adshs_without_bs), " - " , xml_adshs_without_bs)
    print("ZIP adshs without BS: ", len(zip_adshs_without_bs), " - " , zip_adshs_without_bs)
    print("not in xml", xml_adshs_without_bs - zip_adshs_without_bs )


"""
Data:
 BS Test
  - Baseline
   BS Entries in XML:  11474
   BS Entries in ZIP:  10730
   XML adshs without BS:  39  -  {'0001731122-21-000401', '0001376474-21-000052', '0001625285-21-000002', '0000715812-21-000002', '0001052918-21-000070', '0001539816-21-000003', '0001775098-21-000005', '0001078782-21-000032', '0001376474-21-000024', '0001376474-21-000080', '0001213900-21-019311', '0001078782-21-000166', '0001548123-21-000030', '0001376474-21-000025', '0001827855-21-000003', '0001376474-21-000072', '0001193125-21-102032', '0001096906-21-000531', '0001331757-21-000011', '0001564590-21-012829', '0001096906-21-000417', '0001548123-21-000029', '0001587650-21-000010', '0001350420-21-000002', '0001376474-21-000073', '0001552781-21-000008', '0001669374-21-000016', '0001448788-21-000006', '0001096906-21-000191', '0001078782-21-000193', '0001625285-21-000004', '0001376474-21-000053', '0001625285-21-000006', '0001078782-21-000120', '0001078782-21-000058', '0001393905-21-000014', '0001206942-21-000014', '0000100716-21-000020', '0001549983-21-000003'}
   ZIP adshs without BS:  8  -  {'0001669374-21-000016', '0001539816-21-000003', '0001775098-21-000005', '0001437749-21-007013', '0001193125-21-102032', '0000065984-21-000096', '0001587650-21-000010', '0001072627-21-000022'}

  - 1. change -> exclude 'details' 
    ADSH with BS Entries in XML:   5'430
    ADSH with BS Entries in ZIP:   5'462
    BS Entries in XML:            10'977
    BS Entries in ZIP:            10'730
    XML adshs without BS:             40  
    ZIP adshs without BS:              8  
    
  - 2. change -> use max_confident_list, instead conf_2_list
    ADSH with BS Entries in XML:   5'430
    ADSH with BS Entries in ZIP:   5'462
    BS Entries in XML:            10'688
    BS Entries in ZIP:            10'730
    XML adshs without BS:             40 
    ZIP adshs without BS:              8        
    
  - 3. change -> additional keywords (condition)            
    ADSH with BS Entries in XML:   5'431
    ADSH with BS Entries in ZIP:   5'462
    BS Entries in XML:            10'665
    BS Entries in ZIP:            10'730
    XML adshs without BS:             39
    ZIP adshs without BS:              8 
    
    
  - 4. change -> additional keywords
    ADSH with BS Entries in XML:   5'457
    ADSH with BS Entries in ZIP:   5'462
    BS Entries in XML:            10'716
    BS Entries in ZIP:            10'730
    XML adshs without BS:             13
    ZIP adshs without BS:              8   
    
    not in xml {'0001827855-21-000003', '0001213900-21-019311', '0001448788-21-000006', '0001331757-21-000011', '0001625285-21-000004', '0001625285-21-000002', '0001625285-21-000006'}

"""


# Tests
# 1. Adshs vergleichen
# 2. Anzahl Statements vergleichen
# 3. Statement typen vergleichen
# 4. Reihenfolge vergleichen (falls in der richtingen Reihenfolge geschrieben wurde)


if __name__ == '__main__':
    # test_preXmlParsing()
    pass