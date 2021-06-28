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
   1. select all entries in the sec_feeds_table which don't contain a value in the
    column
   warum das downloaded