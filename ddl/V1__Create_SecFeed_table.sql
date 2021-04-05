CREATE TABLE IF NOT EXISTS sec_feeds
(
    accessionNumber PRIMARY KEY,
    sec_feed_file,
    companyName,
    formType,
    filingDate,
    cikNumber,
    fileNumber,
    acceptanceDatetime,
    period,
    assistantDirector,
    assignedSic,
    fiscalYearEnd,
    xbrlInsUrl,
    xbrlCalUrl,
    xbrlDefUrl,
    xbrlLabUrl,
    xbrlPreUrl
)