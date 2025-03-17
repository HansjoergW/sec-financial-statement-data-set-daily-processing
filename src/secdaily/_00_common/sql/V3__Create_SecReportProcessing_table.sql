CREATE TABLE IF NOT EXISTS sec_report_processing
(
    accessionNumber,
    formType,
    filingDate,
    filingDay,
    filingMonth,
    filingYear,
    cikNumber,
    xbrlInsUrl,
    insSize,
    xmlNumFile,
    numParseDate,
    numParseState,
    csvNumFile,

    xbrlPreUrl,
    preSize,
    xmlPreFile,
    preParseDate,
    preParseState,
    csvPreFile,

    xbrlLabUrl,
    labSize,
    xmlLabFile,
    labParseDate,
    labParseState,
    csvLabFile,    

    formatState,
    formatDate,
    numFormattedFile,
    preFormattedFile,

    dailyZipFile,
    processZipDate,
    fiscalYearEnd,
    PRIMARY KEY (accessionNumber)
)
