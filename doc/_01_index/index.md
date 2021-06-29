# Overview
The main steps of processing the xbrl-rss-feed index files are the following:
1. (class SecIndexFileProcessor) download from https://www.sec.gov/Archives/edgar/monthly/index.json the information for the available
   xbrl-rss-feed files and their latest modification date
1. (class SecIndexFileProcessor) check whether one or more index file have to be processed, either because they are new, or their
   latest-modification date has changed
1. (class SecIndexFileProcessor) for evey xbrl-rss-feed file, that has to be processed 
   1. (class SecIndexFileParsing) download the file
   1. (class SecIndexFileParsing) parse the file
      1. extract the fields
       'companyName', 'formType', 'filingDate', 'cikNumber',
       'accessionNumber', 'fileNumber', 'acceptanceDatetime',
       'period', 'assistantDirector', 'assignedSic', 'fiscalYearEnd',
       'xbrlInsUrl', 'xbrlCalUrl', 'xbrlDefUrl', 'xbrlLabUrl', 'xbrlPreUrl'
      1. only consider 10-K and 10-Q reports
      1. return the dataset as a pandas dataframe
   1. (class SecIndexFileProcessor) add entries that are not already present int the sec_feeds table
   1. (class SecIndexFileProcessor) update or add the entry for the xbrl-rss-feed file in the sec_index_file table
1. (class SecIndexFilePostProcessor) Postprocess the entries in the sec_feeds_table
   1. add missing xbrlInsUrl entries
      1. select all entries in the sec_feeds_table which don't contain a value in the column xbrlInsUrl
      1. download the index.json of the selected reports and find the file that ends with "htm.xml"
      1. Update the xbrlInsUrl with the found entry
   1. Check for duplicated entries in the sec_feeds table and mark the duplicates
    

# Notes about Postprocessing
## Missing xbrlInsUrl
When the xbrl information is filed, it is possible that the "numeric" information is delivered in
its own xbrl file. In this case, the entry for a report in the xbrl-rss-feed-file does contain an entry
for "xbrlInsUrl". However, it gets more and more common that the numeric xbrl information is directly coded inside
the main html of a report. In this case, there is no separate file containing the numeric information and hence,
there is no entry for xbrlInsUrl in the xbrl-rss-feed-file for the appropriate report.
However the SEC does create an export for the numeric information from the main html of the report and ends it with
"htm.xml". But in order to find the name/url of that file it is necessary to parse the index.json of that report.

## Duplicated entries
It can happen, that a report (a unique accessionnumber) can be present in two following months with the exact same 
values. It is very rare (only 1 occurence in the Q1 of 2021) and I don't know why this can happen. In this case
the additional entry is marked as a duplicate.


# relevant tables and their purpose
##sec_index_file
Keeps track of the processed xbrl-rss-feed-files. The status contains the "last-modified" of the file (extracted 
from "https://www.sec.gov/Archives/edgar/monthly/index.json"). This is used to detect if there were changes.

##sec_feeds
Tracks the metadata of all of the reports that are found in the xbrl-rss-feed-files
