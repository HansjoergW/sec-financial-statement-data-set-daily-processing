CREATE TABLE IF NOT EXISTS state
(
    attribute TEXT NOT NULL,
    value TEXT,
    date TEXT,
    comment TEXT,
    
    PRIMARY KEY (attribute)
);
