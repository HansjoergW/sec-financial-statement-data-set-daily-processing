-- fileType, -- either num or pre
-- stmt, -- only for pre
-- report, --normalized report,
-- countMatching,
-- countUnequal, -- on both sides, but different
-- countOnlyOrigin, -- just on orign
-- countOnlyDaily, -- just on daily

CREATE TABLE IF NOT EXISTS mass_testing_v2
(
    runId,
    adsh,
    fileType, 
    stmt, 
    report,
    qtr,
    countMatching,
    countUnequal, 
    countOnlyOrigin, 
    countOnlyDaily, 
    tagsUnequal,
    tagsOnlyOrigin,
    tagsOnlyDaily,
    quarterFile,
    dailyFile,

    PRIMARY KEY (adsh, runId, fileType, stmt, report)
);