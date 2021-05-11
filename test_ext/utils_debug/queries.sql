-- csv file einträge löschen
UPDATE sec_report_processing SET preParseState=NULL, preParseDate=NULL,csvPreFile=null, numParseDate=Null, numParseState=Null, csvNumFile=Null;
