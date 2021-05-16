CREATE TABLE IF NOT EXISTS mass_pre_zip_content
(
    adsh,
    qrtrFile,
    stmt,
    report,
    length,
    tagList,
    xmlFile,

    PRIMARY KEY (adsh, report)
);

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

    PRIMARY KEY (adsh, runId)
)