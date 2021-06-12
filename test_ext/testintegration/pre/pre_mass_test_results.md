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
    '0001553350-21-000261'   - role="http://lightwavelogic.com/role/lwlg-bs      BS
                             - role="http://lightwavelogic.com/role/lwlg-bsp     BS inpth

Spezielfälle IS:
 0001193125-21-081336 -> ConsolidatedStatementsOfNetAssets ConsolidatedStatementsOfChangesInNetAssets LiquidationPlan
                         in Liquidation
 0001193125-21-040108 -> in Liquidation   
 0001140361-21-004772 -> in Liquidation
                       
 0001213900-21-009521 -> role und root als BS, obwohl eigentlich IS -> obwohl schon anderes BS vorhanden

Spezialfälle CI
 0000750004-21-000008 -> 2 gültige CIs -> erstes wie IS, mit einem comprehensive Eintrag Länge 35, zweites Länge 8  
 0001453818-21-000008 -> IS nicht korrekt erkannt, daher CI nicht als IS markiert
 
## Fehler in Zip
 0001564590-21-009011 -> EQ inpth wird in Zip als IS inpth markiert 
 0000070866-21-000011 -> BS inpth wird in Zip als CI inpth markiert
 0000074260-21-000021 -> CF inpth in ZIp as CI
 0001564590-21-013460 -> IS as EQ 
 
 
