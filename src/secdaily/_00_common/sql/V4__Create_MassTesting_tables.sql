-- table with content in order to prepare the reports and not the single entries
CREATE TABLE IF NOT EXISTS mass_pre_zip_content
(
    adsh,
    qrtrFile,
    stmt,
    report,
    length,
    tagList,
    xmlFile,
    inpth,

    PRIMARY KEY (adsh, report)
);

-- table with content in order to prepare the reports and not the single entries
CREATE TABLE IF NOT EXISTS mass_pre_parse_xml_data
(
    adsh,
    role,
    root,
    stmt,
    report,
    stmtCompareKey,
    length,
    tagList,
    xmlFile,
    runId,
    inpth,

    PRIMARY KEY (adsh, runId)
)