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


## BS
  Stand 25.05.2021
    ADSH with BS Entries in XML:  5464
    ADSH with BS Entries in ZIP:  5462
    BS Entries in XML:     10740
    BS Entries in ZIP:     10730
    XML adshs without BS:  6  -  {'0001775098-21-000005', '0001193125-21-102032', '0001539816-21-000003', '0001213900-21-019311', '0001669374-21-000016', '0001587650-21-000010'}
    ZIP adshs without BS:  8  -  {'0001775098-21-000005', '0001193125-21-102032', '0001437749-21-007013', '0001539816-21-000003', '0001587650-21-000010', '0001669374-21-000016', '0001072627-21-000022', '0000065984-21-000096'}
    missing in both:       {'0001775098-21-000005', '0001539816-21-000003', '0001193125-21-102032', '0001587650-21-000010', '0001669374-21-000016'}
    only missing in xml  : {'0001213900-21-019311'}
    only missing in zip  : {'0001437749-21-007013', '0000065984-21-000096', '0001072627-21-000022'}

## CP
test_compare_adshs:
  Entries in XML:  5470
  Entries in ZIP:  5464
  
  not in xml:  set()
  not in zip:  {'0001775098-21-000005', '0001539816-21-000003', '0000065984-21-000096', '0001437749-21-007013', '0001587650-21-000010', '0001669374-21-000016'}
  
  Analyse:
    - bis auf einen Eintrag vom Februar sind alle Einträge vom Ende März

test_compare_CP                  
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

  Test 3: PostProcessing für CP eingefügt
  - CP Entries in XML:  5469
  - CP Entries in ZIP:  5464
  - adsh in XML ohne CP: '0000829224-21-000029' -> multiple root nodes in DocumentEntity (Starbucks) 