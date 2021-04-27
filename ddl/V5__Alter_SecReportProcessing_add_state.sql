ALTER TABLE sec_report_processing RENAME COLUMN parseDate TO preParseDate;
ALTER TABLE sec_report_processing ADD numParseDate VARCHAR;
ALTER TABLE sec_report_processing ADD preParseState VARCHAR;
ALTER TABLE sec_report_processing ADD numParseState VARCHAR;