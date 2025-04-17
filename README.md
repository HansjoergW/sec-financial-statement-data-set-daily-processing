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
from secdaily.SecDaily import SecDailyOrchestrator

# Initialize the orchestrator
orchestrator = SecDailyOrchestrator(
    workdir="/path/to/your/data/directory/",
    user_agent_def="Your Company Name yourname@example.com",
    start_year=2024,  # Optional: specify starting year
    start_qrtr=1      # Optional: specify starting quarter
)

# Run the full process
orchestrator.process()
```

### Parameters

- `workdir`: Directory where all data will be stored (including the SQLite database)
- `user_agent_def`: **Required** - Your user agent string for SEC.gov requests. Must follow the format specified in [SEC's EDGAR access requirements](https://www.sec.gov/os/accessing-edgar-data): "Company Name contact@company.com"
- `start_year`: Optional - Year to start processing from (defaults to current year)
- `start_qrtr`: Optional - Quarter to start processing from (defaults to current quarter)

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
```

## Directory Structure of the Created Data

The tool creates the following directory structure in your specified `workdir`:

```
workdir/
├── sec_data.db                # SQLite database for tracking processing
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
└── _4_daily/                  # Daily zip files organized by quarter
    ├── 2024q4/                
    │   ├── 20241001.zip       # Daily zip file
    │   ├── 20241002.zip
    │   └── ...
    └── ...
```

Each daily zip file contains:
- `sub.txt` - Submission information
- `pre.txt` - Presentation information
- `num.txt` - Numeric data

## Limitations

- `num.txt` doesn't contain content for the segments column
- XBRL data embedded in HTML files (approximately 20% of reports) is not processed yet
- Numbering of columns "report" and "line" in `pre.txt` may not be the same as in the quarterly files, but the order should be the same
- The tool throttles requests to SEC.gov to comply with their limit of 10 requests per second

## High-level Process Description

1. **Index Processing**: Parse SEC's index.json to identify new filings
2. **XML Processing**: Download and extract necessary XML files
3. **Data Parsing**: Process the XML files into CSV format (creating initial versions of `num.txt`, `pre.txt`, `lab.txt`)
4. **SEC-style Formatting**: Format the data to match the official SEC dataset structure
5. **Daily Zip Creation**: Package the formatted data into daily zip files

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

## Links

- [Documentation](https://hansjoergw.github.io/sec-financial-statement-data-set-daily-processing/)
- [GitHub Repository](https://github.com/HansjoergW/sec-financial-statement-data-set-daily-processing)
- [Issue Tracker](https://github.com/HansjoergW/sec-financial-statement-data-set-daily-processing/issues)
- [Discussions](https://github.com/HansjoergW/sec-financial-statement-data-set-daily-processing/discussions)
- [Changelog](https://github.com/HansjoergW/sec-financial-statement-data-set-daily-processing/blob/main/CHANGELOG.md)