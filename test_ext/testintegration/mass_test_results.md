# 23.05.2021
## Basic Data Zip File
ADSH -Entries in ZIP:  5464

BS	10730
CF	5956
CI	3073
CP	5464
EQ	7269
IS	5955
UN	448

## Allgemein / Sonderfälle
Keine Reports mit BS, IS, CF, etc.
    '0001193125-21-102032', '0001669374-21-000016' '0001539816-21-000003' '0001775098-21-000005' '0001587650-21-000010'

BS mit CashFlow Role
    0001213900-21-019311 BS: sieht aus als wäre das als CashFlow betitelt!

mit Mulitple RootNodes: 
   CP 0000829224-21-000029 / DocumentEntity (Starbucks)
   EQ 0000920371-21-000042 / EQ skipped report with role http://www.simpsonfg.com/role/ConsolidatedStatementsofStockholdersEquityParenthetical 
   CF 0001254699-21-000005 / CF skipped report with role http://www.qvc.com/role/ConsolidatedStatementsofCashFlows 
   CF 0001628280-21-002278 / CF skipped report with role http://polaris.com/role/ConsolidatedStatementsOfCashFlows     

parentheticals cases werden nicht gefunden
    '0001174947-21-000168'  - xlink:role="http://ruger.com/role/rgr-cbs">
                            - xlink:role="http://ruger.com/role/rgr-cbsp">
    '0001178913-21-000696'  - role="http://solaredge.com/role/sedg-cbs"
                            - role="http://solaredge.com/role/sedg-cbsp"
    '0001206774-21-000530'  - role="http://cassinfo.com/role/cass-cbs1"
                             - role="http://cassinfo.com/role/cass-cbsp1"
    '0001553350-21-000261'   - role="http://lightwavelogic.com/role/lwlg-bs">
                             - role="http://lightwavelogic.com/role/lwlg-bsp">


## BS
Stand 01.06.2021
  ADSH with BS Entries in XML:  5465
  ADSH with BS Entries in ZIP:  5462
  BS Entries in XML       :  10769
  BS Entries in ZIP       :  10730
  XML adshs without BS    :  5  -  {'0001193125-21-102032', '0001539816-21-000003', '0001669374-21-000016', '0001587650-21-000010', '0001775098-21-000005'}
  ZIP adshs without BS    :  8  -  {'0001193125-21-102032', '0001539816-21-000003', '0000065984-21-000096', '0001669374-21-000016', '0001587650-21-000010', '0001437749-21-007013', '0001775098-21-000005', '0001072627-21-000022'}
  missing in both         :  {'0001193125-21-102032', '0001539816-21-000003', '0001669374-21-000016', '0001587650-21-000010', '0001775098-21-000005'}
  only missing in xml     :  set()
  only missing in zip     :  {'0000065984-21-000096', '0001072627-21-000022', '0001437749-21-007013'}
  
  entries with unmatching tags:  (0, 0)
  
  unequal counts:         :  47
  BS reports not in xml   :  4
  BS reports not in zip   :  43
  
  BS not in xml (first 10):                                   report_xml  report_zip  equal
  adsh                 stmt inpth                               
  0001174947-21-000168 BS   1             NaN         1.0  False
  0001178913-21-000696 BS   1             NaN         1.0  False
  0001206774-21-000530 BS   1             NaN         1.0  False
  0001553350-21-000261 BS   1             NaN         1.0  False
  
  BS not in zip (first 10):                                   report_xml  report_zip  equal
  adsh                 stmt inpth                               
  0000007789-21-000018 BS   1             1.0         NaN  False
  0000016918-21-000010 BS   1             1.0         NaN  False
  0000055772-21-000016 BS   1             1.0         NaN  False
  0000065984-21-000096 BS   0             1.0         NaN  False
                            1             1.0         NaN  False
  0000070866-21-000011 BS   1             1.0         NaN  False
  0000077159-21-000016 BS   1             1.0         NaN  False
  0000099780-21-000012 BS   1             1.0         NaN  False
  0000277638-21-000003 BS   1             1.0         NaN  False
  0000310522-21-000156 BS   1             1.0         NaN  False

## CP
Stand 01.06.2021
  ADSH with CP Entries in XML:  5469
  ADSH with CP Entries in ZIP:  5464
  CP Entries in XML       :  5469
  CP Entries in ZIP       :  5464
  XML adshs without CP    :  1  -  {'0000829224-21-000029'}
  ZIP adshs without CP    :  6  -  {'0001539816-21-000003', '0001437749-21-007013', '0001587650-21-000010', '0001669374-21-000016', '0000065984-21-000096', '0001775098-21-000005'}
  missing in both         :  set()
  only missing in xml     :  {'0000829224-21-000029'}
  only missing in zip     :  {'0001539816-21-000003', '0001437749-21-007013', '0001587650-21-000010', '0001669374-21-000016', '0000065984-21-000096', '0001775098-21-000005'}
  
  entries with unmatching tags:  (0, 0)
  
  unequal counts:         :  7
  CP reports not in xml   :  1
  CP reports not in zip   :  6
  
  CP not in xml (first 10):                                   report_xml  report_zip  equal
  adsh                 stmt inpth                               
  0000829224-21-000029 CP   0             NaN         1.0  False
  
  CP not in zip (first 10):                                   report_xml  report_zip  equal
  adsh                 stmt inpth                               
  0000065984-21-000096 CP   0             1.0         NaN  False
  0001437749-21-007013 CP   0             1.0         NaN  False
  0001539816-21-000003 CP   0             1.0         NaN  False
  0001587650-21-000010 CP   0             1.0         NaN  False
  0001669374-21-000016 CP   0             1.0         NaN  False
  0001775098-21-000005 CP   0             1.0         NaN  False
    
