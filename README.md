# SEC Financial Statement Data Set Daily Processing

[![PyPI version](https://badge.fury.io/py/secdaily.svg)](https://badge.fury.io/py/secdaily)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Purpose

The `secdaily` package replicates the quarterly [Financial Statement Datasets](https://www.sec.gov/dera/data/financial-statement-data-sets) from the SEC, but on a daily basis. While the SEC only provides these datasets once per quarter, this tool allows you to:

- Add daily updates by processing new 10-K and 10-Q filings as they become available
- Generate daily zip files in the same format as the official quarterly datasets

This enables financial analysts, researchers, and developers to access structured financial statement data without waiting for the quarterly releases.

## Installation

The package requires Python 3.10 or higher. Install using pip:

```bash
pip install secdaily
```

## Usage

The main entry point is the `SecDailyOrchestrator` class. Here's a basic example:

```python
from secdaily.SecDaily import SecDailyOrchestrator, Configuration

# create the configuration
configuration = Configuration(workdir=workdir_default)


# Initialize the orchestrator
orchestrator = SecDailyOrchestrator(configuration=configuration)

# Run the full process
orchestrator.process(
    start_year=2025,  # Optional: specify starting year (defaults to current year)
    start_qrtr=1      # Optional: specify starting quarter (defaults to current quarter)
)
```

### Configuration Parameters

The configuration class provides the following parameters:

- `user_agent_def`: User agent string for SEC.gov requests. If not provided, a default string will be generated. Must follow the format specified in [SEC's EDGAR access requirements](https://www.sec.gov/os/accessing-edgar-data): "Company Name contact@company.com"
- `workdir`: Working directory for storing all data. Defaults to current directory.
- `xmldir`: Directory for storing XML files. If not provided, defaults to '_1_xml/' under workdir.
- `csvdir`: Directory for storing CSV files. If not provided, defaults to '_2_csv/' under workdir.
- `formatdir`: Directory for storing SEC-style formatted files. If not provided, defaults to '_3_secstyle/' under workdir.
- `dailyzipdir`: Directory for storing daily zip files. If not provided, defaults to '_4_daily/' under workdir.
- `quarterzipdir`: Directory for storing quarterly zip files. If not provided, defaults to '_5_quarter/' under workdir.
- `clean_intermediate_files`: Flag to clean up intermediate files during housekeeping. Defaults to False.
- `clean_db_entries`: Flag to clean up database entries during housekeeping. Defaults to False.
- `clean_daily_zip_files`: Flag to clean up daily zip files during housekeeping. Defaults to False.
- `clean_quarter_zip_files`: Flag to clean up quarterly zip files during housekeeping. Defaults to False.


### How to use it
Normally, you will use the "orginial" quarterly files from the SEC [Financial Statement Datasets](https://www.sec.gov/dera/data/financial-statement-data-sets) as a starting point. Therefore, you will set the "start_year" and "start_qrtr" parameters to the quarter of the first quarter that is missing at SEC. For example, if quarterly up to 2024Q4 are available on the SEC site, you will set the "start_year" to 2025 and the "start_qrtr" to 1 in order to download and process the daily available xml files and transform them into the same format as the SEC quarterly files. 

The quarterly zip file from the sec is usually available two to three weeks after the quarter end. 

As soon as a new quarter zip file on SEC is available, you can then adjust the startyear and startqrtr parameters to the next quarter. Dpending on the configuration, intermediate files, database entries, and zip files can be cleaned up.

Since reports are filed daily on the SEC, you will run the process daily to be always up-to-date with the latest available reports.


## High-level Process Description

1. **Index Processing**: Parse SEC's index.json to identify new filings
2. **XML Processing**: Download and extract necessary XML files
3. **Data Parsing**: Process the XML files into CSV format (creating initial versions of `num.txt`, `pre.txt`, `lab.txt`)
4. **SEC-style Formatting**: Format the data to match the official SEC dataset structure
5. **Daily Zip Creation**: Package the formatted data into daily zip files
6. **Quarterly Zip Creation**: Package the daily zip files into quarterly zip files
7. **Housekeeping**: Clean up intermediate files, database entries, and zip files based on the provided configuration


### Individual Process Steps

You can also run individual parts of the process:

```python
# Only process index data
orchestrator.process_index_data()

# Only process XML data
orchestrator.process_xml_data()

# Only create SEC-style formatted files
orchestrator.create_sec_style()

# Only create daily zip files
orchestrator.create_daily_zip()

# Only create quarter zip files
orchestrator.create_quarter_zip()

# Only perform housekeeping
# housekeeps everything before the start quarter
orchestrator.housekeeping(start_qrtr_info=QuarterInfo(year=2025, qrtr=1))
```

## Directory Structure of the Created Data

The tool creates the following directory structure in your specified `workdir`:

```
workdir/
├── sec_processing.db          # SQLite database for tracking processing
├── _1_xml/                    # Downloaded XML files
│   ├── 2024q4/  
│   │   ├── 2024-10-01/
│   │   │   ├── xyz_htm.xml.zip
│   │   │   ├── xyz_pre.xml.zip
│   │   │   ├── xyz_lab.xml.zip
│   │   │   └── ...
│   │   └── ...
│   └── ...                    
├── _2_csv/                    # Parsed CSV files
│   ├── 2024q4/  
│   │   ├── 2024-10-01/
│   │   │   ├── xyz_num.csv.zip
│   │   │   ├── xyz_pre.csv.zip
│   │   │   ├── xyz_lab.csv.zip
│   │   │   └── ...
│   │   └── ...
│   └── ...                    
├── _3_secstyle/               # SEC-style formatted files
│   ├── 2024q4/  
│   │   ├── 2024-10-01/
│   │   │   ├── xyz_num.csv.zip
│   │   │   ├── xyz_pre.csv.zip
│   │   │   └── ...
│   │   └── ...
│   └── ...                    
├── _4_daily/                  # Daily zip files
│   ├── 2024q4/                
│   │   ├── 20241001.zip       
│   │   ├── 20241002.zip
│   │   └── ...
│   └── ...
└── _5_quarter/                # Quarterly zip files
    ├── 2024q4.zip
    ├── 2025q1.zip
    └── ...
```

Each daily and quarterly zip file contains:
- `sub.txt` - Submission information
- `pre.txt` - Presentation information
- `num.txt` - Numeric data

## Limitations

- `num.txt` doesn't contain content for the segments column
- XBRL data embedded in HTML files (approximately 20% of reports) is not processed yet
- Numbering of columns "report" and "line" in `pre.txt` may not be the same as in the quarterly files, but the order should be the same
- The tool throttles requests to SEC.gov to comply with their limit of 10 requests per second
- sub.txt only contains a subset of the information available in the quarterly files from sec.gov

## Robustness Features

- Implements retry mechanisms for failed downloads
- Uses a SQLite database to track processing state, allowing for safe restarts
- Throttles requests to comply with SEC.gov's rate limits
- Stores downloaded and created files in a compressed format to conserve disk space
- Uses parallel processing where appropriate for improved performance

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## SEC Financial Statement Data Sets Tools (secfsdstools)
Also check out the [SEC Financial Statement Data Sets Tools](https://github.com/HansjoergW/secfsdstools) project.

## Links

- [Documentation](https://hansjoergw.github.io/sec-financial-statement-data-set-daily-processing/)
- [GitHub Repository](https://github.com/HansjoergW/sec-financial-statement-data-set-daily-processing)
- [Issue Tracker](https://github.com/HansjoergW/sec-financial-statement-data-set-daily-processing/issues)
- [Discussions](https://github.com/HansjoergW/sec-financial-statement-data-set-daily-processing/discussions)
- [Changelog](https://github.com/HansjoergW/sec-financial-statement-data-set-daily-processing/blob/main/CHANGELOG.md)