# Overview
The main steps of parsing the pre and num-xml files are the following.
1. (class SecXmlFilePreProcessor) find new entries in the sec_feeds table and copy them to the sec_report_processing table
1. (class SecXmlFileDownloader) find entries in the sec_report_processing_table for which the pre and num xml files were not already downloaded
and download these files
1. (class SecXmlFileParser) find entries in the sec_report_processing_table for which the pre and num xml files were not already parsed and parse them   

# Notes
## Notes about Downloader
The Downloader ensures that a maximum of 8 files per seconds are downloaded, since the SEC restricts access to their
site to 10requests per second. Moreover, if a single download request fails, the logic tries six times, before giving up this
first attempt to download the file. 
However, there is a second loop that checks whether all desired files could have been downloaded. If there are files 
that couldn't be downloaded in a first attempt, the logic tries to download these files again. These loop is repeated
until either all files were finally downloaded or if no new files were downloaded in a loop.

## Notes about Parser
parallel 

# Relevant tables and their purpose

##sec_feeds
source to copy the new entries into the sec_report_processing table

##sec_report_processing
keeps track of the parsing and transformation process.
