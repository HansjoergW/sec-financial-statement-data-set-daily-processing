# Creation of Sub content

## Problems
### name 
It's not clear based on what the name is cleaned. mainly it is toUpper and the removal of \. 
However, there are four special cases:
adsh                    Name Zip                Name Xml
0000320193-21-000010    APPLE INC               APPLE INC.        
0001654954-21-002287    BK TECHNOLOGIES         BK TECHNOLOGIES CORP
0000004127-21-000013    SKYWORKS SOLUTIONS INC  SKYWORKS SOLUTIONS, INC.
0000003570-21-000039    CHENIERE ENERGY INC     CHENIERE ENERGY, INC.

It is not clear what the reules are, since there are entries which end with "INC.", or ", INC"
so it is not possible to just remove '.' and ',' as well. These would need to be hardcoded numbers.


### sic
There 15 entries which show different sic numbers, than the ones presented in the feed xml

### period
there are two entries which show a different period

### fye
there are 29 entries not matching. Some zip entries seem to be wrong. If it is a 10-Q, 
then the period end shouldn't be the fye ending. 
this seems to be corrected in some way b
but this is also true in the opposite direction. i


### fy
fy -> falls 10-K im ersten Quartal endet, dann von vorherigem Jahr

für Qs nicht klar. es gibt wiedersprüchliches.
z.B. beide haben Q3 Ende Jahr, aber unterschiedlichen Jahres Fokus
0001489096-21-000029,10-Q,Q3,2020,0331,20201231
0001019056-21-000102,10-Q,Q3,2021,0331,20201231

Bsp: Modular Medical, Inc., Quartale stimmen nicht mit Jahr
0001019056-20-000470 Q1 2020-06-30  2021
0001019056-20-000551 Q2 2020-09-30  2021
0001019056-21-000102 Q3 2020-12-31  2021
0001019056-21-000387 FY 2021-03-31  2020


### fp
22 Einträge stimmen nicht überein.
- Fälle, bei denen kein fye vorhanden ist (0000) (Q0)
- Fälle, bei denen in 10-Q gleiches PeriodenEnde wie fye hat (Q4)


## sonstiges

laut Kapitel 6 in EFM können verschiedene Angaben aus den Fillings an folgenden Stellen stehen

AmendmentDescription 6.5.20 dei
DocumentPeriodEndDate 6.5.20 cover
DocumentType 6.5.20 dei
AmendmentFlag 6.5.20 dei

DocumentFiscalPeriodFocus 6.5.20 dei
DocumentFiscalYearFocus 6.5.20 dei

EntityCurrentReportingStatus 6.5.21 cover
EntityFilerCategory 6.5.21 cover
EntityPublicFloat 6.5.21 cover
EntityRegistrantName 6.5.21 cover
EntityVoluntaryFilers 6.5.21 cover
EntityWellKnownSeasonedIssuer 6.5.21 cover

CurrentFiscalYearEndDate 6.5.21 dei