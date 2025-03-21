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
);


-- fileType, -- either num or pre
-- stmt, -- only for pre
-- report, --normalized report,
-- countMatching,
-- countUnequal, -- on both sides, but different
-- countOnlyOrigin, -- just on orign
-- countOnlyDaily, -- just on daily

CREATE TABLE IF NOT EXISTS mass_testing_v2
(
    adsh,
    qtr,
    fileType, 
    stmt, 
    report,
    countMatching,
    countUnequal, 
    countOnlyOrigin, 
    countOnlyDaily, 
    tagsUnequal,
    tagsOnlyOrigin,
    tagsOnlyDaily,
    runId,
    quarterFile,
    dailyFile,

    PRIMARY KEY (adsh, runId)
);