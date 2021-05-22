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


def filter_for_adsh_and_statement(df: pd.DataFrame, adshs: Set[str], stmt: str) -> pd.DataFrame:
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

    # we want to have all reports in the zip also present in the xml
    # however, we do not care if there additional entries present
    assert len(not_in_xml) == 0


def test_compare_CP():
    xml_cp_df = filter_for_adsh_and_statement(xml_data_df, adshs_in_both, 'CP')
    zip_cp_df = filter_for_adsh_and_statement(zip_data_df, adshs_in_both, 'CP')

    xml_adshs_with_cp = set(xml_cp_df.adsh.unique().tolist())
    xml_adshs_without_cp = adshs_in_xml - xml_adshs_with_cp

    print("")
    print("CP Entries in XML: ", len(xml_cp_df))
    print("CP Entries in ZIP: ", len(zip_cp_df))
    print("XML adshs without CP: ", xml_adshs_without_cp)


"""
Data:
test_compare_adshs:
  Entries in XML:  5470
  Entries in ZIP:  5464
  not in xml:  set()
  not in zip:  {'0001775098-21-000005', '0001539816-21-000003', '0000065984-21-000096', '0001437749-21-007013', '0001587650-21-000010', '0001669374-21-000016'}
  
  Analyse:
    - bis auf einen Eintrag vom Februar sind alle Einträge vom Ende März

test_compare_CP                  
  CP Entries in XML:  6282
  CP Entries in ZIP:  5464
  XML adshs without CP:  {'0001376986-21-000007', '0000829224-21-000029'}
  
  Test 1: initial
  - Es gibt Einträge, die haben über 100 CP entries: 0001437107-21-000018, 0001393612-21-000014
    Total haben 179 Einträge mehr al 1 CP
  - In XML sind für 5668 Einträge CP Einträge vorhanden, für 2 adshs gibt es keine:  
          '0001376986-21-000007' -> "company" role and root-node
          '0000829224-21-000029' -> multiple root nodes in DocumentEntity (Starbucks)
          
  Test 2: coverabstract, coverpage und deidocument als neue schlüssel für CP
  - Es gibt neu nur noch  3 Einträge mit je 3 CPs: 0000089089-21-000012, 0000898174-21-000006, 0001829126-21-002055
                    und  13 Einträge mit je 2 CPs: z.B. 0000031791-21-000003, 0000039911-21-000021, 0000040211-21-000018, 0000842517-21-000069
  - für 4 Einträge wurden keine CP gefunden: 
         '0000916365-21-000052', '0001702744-21-000011', '0000773141-21-000024'  
         '0000829224-21-000029' -> multiple root nodes in DocumentEntity (Starbucks) 


-> es wird ein weg benötigt, um prinzipiell roles zu ignorieren..
    zb. gibt es coverpagenotes, coverpagetable, coverpagedetails.. 
    das kann aber auch wieder nur als zusätzliche extensions vorhanden sein
    -> erster versuch hat aber nichts gebracht.. 
    
-> es mus snoch gerpüft werden, ob eventuell daten aus reports zusammengefügt werden


"""


# Tests
# 1. Adshs vergleichen
# 2. Anzahl Statements vergleichen
# 3. Statement typen vergleichen
# 4. Reihenfolge vergleichen (falls in der richtingen Reihenfolge geschrieben wurde)


if __name__ == '__main__':
    # test_preXmlParsing()
    pass