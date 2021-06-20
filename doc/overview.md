https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet

# Purpose
The purpose of this project is to download new 10-K and 10-Q reports from edgar at sec.gov and parse and 
preprocess these xml files in a way, so that structure of the resulting csv files is similar
to the stracture of the "Financial Statement Datasets" from the sec.gov.
While the "Financial Statement Dataset" is only provided once for every quarter,
this project has the goal to provide the same data on a daily basis.

# Highlevel Process Description
The implementation is "robust". It uses several fail-over and retry measures to ensure that code can
run automatically without the need of manual restarts. However, should it be necessary, it also isn't
a problem to restart process manually. It also ensures the the access to the sec.gov site is throttled
(there is a limit of 10 request per second) and the logic uses parallel processing if meaningful.

In order to keep track of the different steps of the process, a simple SQLite database is used.

The main steps of the process are as follows:
1. check https://www.sec.gov/Archives/edgar/monthly/index.json for a new monthly file or an update on an existing
   monthly file
2. if there are new and or updated monthly files, download and parse them.
3. add the meta information for new 10k and 10q reports to the appropriate table
4. select unprocessed reports and create appropriate entries in the processing table
5. select reports for which the xml-files have not been downloaded and download this files
6. select reports for which the downloaded xml-files have not been parsed already and parse them
7. for every filing day, create a new zipfile containing all the information for all reports which were
   filed on that day. use the same structure as used in the "Financial Statement Data Sets"

# Folder content of the Project
1. ddl <br>
the ddl folder contains the flyway scripts to setup the used SQLite DB.
1. doc <br>
the doc folder contains the documentation of the project



process overview / highlevel
folder content
setup
- conda env
- flyway script








# Overview
![overview](Class-Overview.png)

## Data
### FeedFiles xbrlrss-<yyyy>-<mm>.xml
Enthalten items, welche edgar:xbrlFiling infos enthalten.
- companyName
- formType
- filingDate
- cikNumber
- accessionNumber
- fileNumber
- acceptanceDtetime
- period
- assistantDirector
- assignedSic
- fiscalYearEnd
- List: xbrlFiles
 
Wichtig: 
- Es können noch die letzten Einträge des vorherigen Monats vorhanden sein.
- selten ist ein Eintrag in 2 Monaten vorhanden


## DB
### "sec_index_files"
Behält die Übersicht, welche monatlichen Index Files verarbeitet worden sind und welches File das aktuelle ist.

### "sec_feeds"
|column|description|
|---|---|
|companyname||
|formtype||
|filingDate||
|cikNumber||
|accessionNumber||
|fileNumber||
|acceptanceDatetime||
|period||
|assistantDirector||
|assignedSic||
|fiscalYearEnd||
|xbrlInsUrl||
|xbrlCalUrl||
|xbrlDefUrl||
|xbrlLabUrl||
|xbrlPreUrl||

- Es gibt Tage, an denen werden massiv mehr Reports angereicht, als an anderen
SELECT "filingDate", COUNT(*) FROM sec_feeds GROUP BY "filingDate";

### "sec_report_processing"
Verfolgt die Verarbeitung der einzelnen xml-daten Files. 


## Classes
### SecProcessingOrchestrator

Ist verantwortlich für das Bereitstellen der Daten. Dieses geschieht in mehreren Schritten:
1. Die Informationen der Filings müssen runtergeladen und in der Tabelle sec_feeds ergänzt werden.
2. Diese Filingsdaten müssen mit den fehlenden "num"-urls ergänzt werden.
3. Noch nicht verarbeitete Einträge müssen runtergeladen und geparsed werden. 
    1. pro Tag werden die Daten aller Firmen in ein eigenes Verzeichnis gespeichert (evtl. gezipt)
    2. In der Tabelle wird eingetragen, welches Filing verarbeitet wurde und an welchem Tag die Verarebeitung stattfand
4. Es muss berechnet werden, welche Tage sich verändert haben. entsprechend müssen DeltaFiles generiert werden.
    1. Frage: sollen die DeltaFiles verschiedene filingdates beinhaltet können, also ist das DeltaFile auf das Verarbeitungsdatum bezogen? das wäre vlt. am einfachsten
    2. Es könnte auch geprüft werden, ob FilingDates zeitnah verarbeitet werden
    
    
