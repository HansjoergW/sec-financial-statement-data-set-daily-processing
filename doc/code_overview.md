https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet

# Overview
The main part of the code is subdivided into 3 part: 01_index, 02_xml, 03_dailyzip. Each of this part is reponsible for a 
major step of the whole process.

The first part "01_index" is responsible to check for newly filed reports, gathering, and storing the metainformation
of these reports.
The second part "02_xml" downloads and parses the xml files containing the information of the reports. The parsed results
are stored as CSV files which use the same structure as the Financial Statement Datasets of the sec.gov.
Finally, the third part creates for every day a zip file of the reports that were filed on that day. Again, the structure
of this file is similar to the quarterly zip files of the Financial Statement Datasets. 

Detailed documentation is available in the subfolders of the doc folder.


# General Aspects
## Robustness
A very important aspect of the code is to be robust in several ways. First, since there will be a alot of url requests
it is very likely, that a few of them will fail. Therefore, if a request fails, the logic repeats the call up to six 
times until it lets the call fail. Moreover, every major step repeats itself again, if there were failed requests.
Furthermore, every major step stores its state in SQLite tables, therefore ensuring that the process can be restarted
over and over again without processing items that have already been processed.

## Throttling
The sec.gov limits the calls from the same IP-Adress to 10 calls per second. If more than 10 calls per seconds are
executed from the same IP, the sec.gov site will start to block this calls with a 403 error. The code throttles the
maximum requests per second, and, as written above, also repeats calls if they should have failed.

## Conserving disk space
Since a lot of data will be downloaded, this data will be stored always in a compressed manner.


# Ensuring quality
## Unit Testing
...

## Mass Testing
As stated in the README.md, the main goal of the project is to provide daily updates of filed 10-K and 10-Q reports
in the same format used in the quartery-zip files of the Financial Statement Datasets.
It is not possible to quarantee that the produced data will be 100% identical. However, at the end of each quarter,
the produced data can be compared with content of the quarterly-zip files and differences are reported. 
The code to produce that report is inside the test_ext folder inside the testintegration package. So far, a similarity
of approximately 99.9% has been reached.