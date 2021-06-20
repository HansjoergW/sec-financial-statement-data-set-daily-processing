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
This folder contains the flyway scripts to setup the used SQLite DB.
1. doc <br>
This folder contains the documentation of the project.
1. src <br>
The source code of the project.
1. test <br>
Unit Tests
1. test_ext <br>
"Extented" testing, contains three subfolders:
    1. testintegration <br>
    Mainly contains "mass-testing" code. This is code that is used to compare the parse content with the 
    original content of the "Financial Statement Data Sets" Zip-Files. 
    1. trials <br> 
    A Sandbox to try out different things and with code that might be worth to keep 
    1. utils_debug <br>
    Some code the helps to simplify debugging of parsing issues 


# Setup and first run

setup
- conda env
- flyway script

setup without flyway
