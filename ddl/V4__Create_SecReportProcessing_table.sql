CREATE TABLE IF NOT EXISTS sec_report_processing
(
    accessionNumber,
    formType,
    filingDate,
    cikNumber,
    xbrlInsUrl,
    xbrlPreUrl,
    xmlNumFile,
    xmlPreFile,
    parseDate,
    csvPreFile,
    csvNumFile,
    PRIMARY KEY (accessionNumber)
)
