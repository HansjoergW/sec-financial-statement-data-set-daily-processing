import os
import shutil
import sqlite3
import tempfile
import zipfile
from unittest.mock import MagicMock

import pytest

from secdaily._00_common.BaseDefinitions import QuarterInfo
from secdaily._06_cleanup.db.HousekeepingDataAccess import HousekeepingDataAccess, ReportToCleanup
from secdaily._06_cleanup.Housekeeping import Housekeeper


@pytest.fixture
def test_dirs():
    """Create temporary directories for testing."""
    temp_dir = tempfile.mkdtemp()

    # Create directory structure
    xml_dir = os.path.join(temp_dir, "_1_xml")
    csv_dir = os.path.join(temp_dir, "_2_csv")
    secstyle_dir = os.path.join(temp_dir, "_3_secstyle")
    daily_zip_dir = os.path.join(temp_dir, "_4_daily")
    quarter_zip_dir = os.path.join(temp_dir, "_5_quarter")

    os.makedirs(xml_dir, exist_ok=True)
    os.makedirs(csv_dir, exist_ok=True)
    os.makedirs(secstyle_dir, exist_ok=True)
    os.makedirs(daily_zip_dir, exist_ok=True)
    os.makedirs(quarter_zip_dir, exist_ok=True)

    # Create quarter directories in daily_zip_dir
    os.makedirs(os.path.join(daily_zip_dir, "2022q4"), exist_ok=True)
    os.makedirs(os.path.join(daily_zip_dir, "2023q1"), exist_ok=True)
    os.makedirs(os.path.join(daily_zip_dir, "2023q2"), exist_ok=True)

    yield {
        "temp_dir": temp_dir,
        "xml_dir": xml_dir,
        "csv_dir": csv_dir,
        "secstyle_dir": secstyle_dir,
        "daily_zip_dir": daily_zip_dir,
        "quarter_zip_dir": quarter_zip_dir,
    }

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def test_db():
    """Create a temporary database for testing."""
    db_file = tempfile.mktemp(suffix=".db")

    # Create database and tables
    conn = sqlite3.connect(db_file)
    conn.execute(
        """
        CREATE TABLE sec_reports (
            accessionNumber TEXT,
            sec_feed_file TEXT,
            formType TEXT,
            filingDate TEXT,
            filingMonth INTEGER,
            filingYear INTEGER,
            cikNumber TEXT,
            PRIMARY KEY (accessionNumber, sec_feed_file)
        )
    """
    )

    conn.execute(
        """
        CREATE TABLE sec_report_processing (
            accessionNumber TEXT,
            formType TEXT,
            filingDate TEXT,
            filingDay INTEGER,
            filingMonth INTEGER,
            filingYear INTEGER,
            cikNumber TEXT,
            xmlNumFile TEXT,
            xmlPreFile TEXT,
            xmlLabFile TEXT,
            csvNumFile TEXT,
            csvPreFile TEXT,
            csvLabFile TEXT,
            numFormattedFile TEXT,
            preFormattedFile TEXT,
            dailyZipFile TEXT,
            PRIMARY KEY (accessionNumber)
        )
    """
    )

    # Insert test data
    conn.execute(
        """
        INSERT INTO sec_reports 
        (accessionNumber, sec_feed_file, formType, filingDate, filingMonth, filingYear, cikNumber)
        VALUES 
        ('0001234567-22-000001', 'feed1.txt', '10-K', '2022-12-15', 12, 2022, '0001234567'),
        ('0001234567-23-000002', 'feed2.txt', '10-K', '2023-01-15', 1, 2023, '0001234567'),
        ('0001234567-23-000003', 'feed3.txt', '10-K', '2023-04-15', 4, 2023, '0001234567')
    """
    )

    conn.execute(
        """
        INSERT INTO sec_report_processing 
        (accessionNumber, formType, filingDate, filingDay, filingMonth, filingYear, cikNumber,
         xmlNumFile, xmlPreFile, xmlLabFile, csvNumFile, csvPreFile, csvLabFile,
         numFormattedFile, preFormattedFile, dailyZipFile)
        VALUES 
        ('0001234567-22-000001', '10-K', '2022-12-15', 15, 12, 2022, '0001234567',
         'xml_num_1.xml', 'xml_pre_1.xml', 'xml_lab_1.xml', 
         'csv_num_1.csv', 'csv_pre_1.csv', 'csv_lab_1.csv',
         'num_fmt_1.txt', 'pre_fmt_1.txt', 'daily_1.zip'),
        ('0001234567-23-000002', '10-K', '2023-01-15', 15, 1, 2023, '0001234567',
         'xml_num_2.xml', 'xml_pre_2.xml', 'xml_lab_2.xml', 
         'csv_num_2.csv', 'csv_pre_2.csv', 'csv_lab_2.csv',
         'num_fmt_2.txt', 'pre_fmt_2.txt', 'daily_2.zip'),
        ('0001234567-23-000003', '10-K', '2023-04-15', 15, 4, 2023, '0001234567',
         'xml_num_3.xml', 'xml_pre_3.xml', 'xml_lab_3.xml', 
         'csv_num_3.csv', 'csv_pre_3.csv', 'csv_lab_3.csv',
         'num_fmt_3.txt', 'pre_fmt_3.txt', 'daily_3.zip')
    """
    )

    conn.commit()
    conn.close()

    yield db_file

    # Cleanup
    if os.path.exists(db_file):
        os.remove(db_file)


def create_test_files(test_dirs, file_paths):
    """Create test files at the specified paths."""
    for file_path in file_paths:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Create empty file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("Test content")


def create_test_zip(zip_path, content="Test content"):
    """Create a test zip file."""
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(zip_path), exist_ok=True)

    # Create zip file with test content
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("test.txt", content)


def test_cleanup_processing_files(test_dirs):
    """Test removing temporary processing files."""
    # Create test files
    xml_files = [
        os.path.join(test_dirs["xml_dir"], "2022q4", "xml_num_1.xml"),
        os.path.join(test_dirs["xml_dir"], "2022q4", "xml_pre_1.xml"),
        os.path.join(test_dirs["xml_dir"], "2023q1", "xml_num_2.xml"),
        os.path.join(test_dirs["xml_dir"], "2023q2", "xml_num_3.xml"),
    ]

    csv_files = [
        os.path.join(test_dirs["csv_dir"], "2022q4", "csv_num_1.csv"),
        os.path.join(test_dirs["csv_dir"], "2022q4", "csv_pre_1.csv"),
        os.path.join(test_dirs["csv_dir"], "2023q1", "csv_num_2.csv"),
        os.path.join(test_dirs["csv_dir"], "2023q2", "csv_num_3.csv"),
    ]

    secstyle_files = [
        os.path.join(test_dirs["secstyle_dir"], "2022q4", "num_fmt_1.txt"),
        os.path.join(test_dirs["secstyle_dir"], "2022q4", "pre_fmt_1.txt"),
        os.path.join(test_dirs["secstyle_dir"], "2023q1", "num_fmt_2.txt"),
        os.path.join(test_dirs["secstyle_dir"], "2023q2", "num_fmt_3.txt"),
    ]

    create_test_files(test_dirs, xml_files + csv_files + secstyle_files)

    # Create mock reports
    reports = [
        ReportToCleanup(
            accessionNumber="0001234567-22-000001",
            filingYear=2022,
            filingMonth=12,
            filingDay=15,
            xmlNumFile=xml_files[0],
            xmlPreFile=xml_files[1],
            csvNumFile=csv_files[0],
            csvPreFile=csv_files[1],
            numFormattedFile=secstyle_files[0],
            preFormattedFile=secstyle_files[1],
        )
    ]

    # Create mock data access
    mock_db = MagicMock()
    mock_db.find_reports_before_quarter.return_value = reports

    # Create housekeeper with start quarter 2023q1
    housekeeper = Housekeeper(
        start_qrtr_info=QuarterInfo(year=2023, qrtr=1),
        xml_dir=test_dirs["xml_dir"],
        csv_dir=test_dirs["csv_dir"],
        secstyle_dir=test_dirs["secstyle_dir"],
        daily_zip_dir=test_dirs["daily_zip_dir"],
        quarter_zip_dir=test_dirs["quarter_zip_dir"],
        db_manager=mock_db,
    )

    # Run cleanup
    files_removed = housekeeper.cleanup_processing_files()

    # Check that files before 2023q1 were removed
    assert files_removed == 6
    assert not os.path.exists(xml_files[0])
    assert not os.path.exists(xml_files[1])
    assert not os.path.exists(csv_files[0])
    assert not os.path.exists(csv_files[1])
    assert not os.path.exists(secstyle_files[0])
    assert not os.path.exists(secstyle_files[1])

    # Check that files from 2023q1 and later still exist
    assert os.path.exists(xml_files[2])
    assert os.path.exists(xml_files[3])
    assert os.path.exists(csv_files[2])
    assert os.path.exists(csv_files[3])
    assert os.path.exists(secstyle_files[2])
    assert os.path.exists(secstyle_files[3])


def test_cleanup_db_entries(test_db):
    """Test removing database entries."""
    # Create data access with test database
    db_manager = HousekeepingDataAccess(work_dir="")
    db_manager.database = test_db

    # Create housekeeper with start quarter 2023q1
    housekeeper = Housekeeper(
        start_qrtr_info=QuarterInfo(year=2023, qrtr=1),
        xml_dir="",
        csv_dir="",
        secstyle_dir="",
        daily_zip_dir="",
        quarter_zip_dir="",
        db_manager=db_manager,
    )

    # Run cleanup
    entries_removed = housekeeper.cleanup_db_entries()

    # Check that entries before 2023q1 were removed
    assert entries_removed == 1

    # Verify database state
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()

    # Check sec_reports table
    cursor.execute("SELECT COUNT(*) FROM sec_reports")
    assert cursor.fetchone()[0] == 2

    cursor.execute("SELECT accessionNumber FROM sec_reports")
    accession_numbers = [row[0] for row in cursor.fetchall()]
    assert "0001234567-22-000001" not in accession_numbers
    assert "0001234567-23-000002" in accession_numbers
    assert "0001234567-23-000003" in accession_numbers

    # Check sec_report_processing table
    cursor.execute("SELECT COUNT(*) FROM sec_report_processing")
    assert cursor.fetchone()[0] == 2

    cursor.execute("SELECT accessionNumber FROM sec_report_processing")
    accession_numbers = [row[0] for row in cursor.fetchall()]
    assert "0001234567-22-000001" not in accession_numbers
    assert "0001234567-23-000002" in accession_numbers
    assert "0001234567-23-000003" in accession_numbers

    conn.close()


def test_cleanup_quarter_zip_files(test_dirs):
    """Test removing quarter zip files."""
    # Create test quarter zip files
    quarter_zips = [
        os.path.join(test_dirs["quarter_zip_dir"], "2022q3.zip"),
        os.path.join(test_dirs["quarter_zip_dir"], "2022q4.zip"),
        os.path.join(test_dirs["quarter_zip_dir"], "2023q1.zip"),
        os.path.join(test_dirs["quarter_zip_dir"], "2023q2.zip"),
    ]

    for zip_path in quarter_zips:
        create_test_zip(zip_path)

    # Create housekeeper with start quarter 2023q1
    housekeeper = Housekeeper(
        start_qrtr_info=QuarterInfo(year=2023, qrtr=1),
        xml_dir=test_dirs["xml_dir"],
        csv_dir=test_dirs["csv_dir"],
        secstyle_dir=test_dirs["secstyle_dir"],
        daily_zip_dir=test_dirs["daily_zip_dir"],
        quarter_zip_dir=test_dirs["quarter_zip_dir"],
        db_manager=MagicMock(),
    )

    # Run cleanup
    files_removed = housekeeper.cleanup_quarter_zip_files()

    # Check that files before 2023q1 were removed
    assert files_removed == 2
    assert not os.path.exists(quarter_zips[0])
    assert not os.path.exists(quarter_zips[1])

    # Check that files from 2023q1 and later still exist
    assert os.path.exists(quarter_zips[2])
    assert os.path.exists(quarter_zips[3])


def test_cleanup_daily_zip_files(test_dirs):
    """Test removing daily zip files."""
    # Create test daily zip files
    daily_zips = [
        os.path.join(test_dirs["daily_zip_dir"], "2022q4", "20221201.zip"),
        os.path.join(test_dirs["daily_zip_dir"], "2022q4", "20221215.zip"),
        os.path.join(test_dirs["daily_zip_dir"], "2023q1", "20230115.zip"),
        os.path.join(test_dirs["daily_zip_dir"], "2023q2", "20230415.zip"),
    ]

    for zip_path in daily_zips:
        create_test_zip(zip_path)

    # Create housekeeper with start quarter 2023q1
    housekeeper = Housekeeper(
        start_qrtr_info=QuarterInfo(year=2023, qrtr=1),
        xml_dir=test_dirs["xml_dir"],
        csv_dir=test_dirs["csv_dir"],
        secstyle_dir=test_dirs["secstyle_dir"],
        daily_zip_dir=test_dirs["daily_zip_dir"],
        quarter_zip_dir=test_dirs["quarter_zip_dir"],
        db_manager=MagicMock(),
    )

    # Run cleanup
    files_removed = housekeeper.cleanup_daily_zip_files()

    # Check that files before 2023q1 were removed
    assert files_removed == 2
    assert not os.path.exists(daily_zips[0])
    assert not os.path.exists(daily_zips[1])
    assert not os.path.exists(os.path.join(test_dirs["daily_zip_dir"], "2022q4"))

    # Check that files from 2023q1 and later still exist
    assert os.path.exists(daily_zips[2])
    assert os.path.exists(daily_zips[3])
    assert os.path.exists(os.path.join(test_dirs["daily_zip_dir"], "2023q1"))
    assert os.path.exists(os.path.join(test_dirs["daily_zip_dir"], "2023q2"))


def test_process_combined_options(test_dirs, test_db):
    """Test running the process method with multiple options."""
    # Create test files
    xml_file = os.path.join(test_dirs["xml_dir"], "xml_num_1.xml")
    create_test_files(test_dirs, [xml_file])

    # Create test quarter zip files
    quarter_zip = os.path.join(test_dirs["quarter_zip_dir"], "2022q4.zip")
    create_test_zip(quarter_zip)

    # Create test daily zip files
    daily_zip_dir = os.path.join(test_dirs["daily_zip_dir"], "2022q4")
    os.makedirs(daily_zip_dir, exist_ok=True)
    daily_zip = os.path.join(daily_zip_dir, "20221215.zip")
    create_test_zip(daily_zip)

    # Create data access with test database
    db_manager = HousekeepingDataAccess(work_dir="")
    db_manager.database = test_db

    # Create mock for find_reports_before_quarter to return a report with our test file
    original_find_reports = db_manager.find_reports_before_quarter

    def mock_find_reports(start_qrtr_info):
        reports = original_find_reports(start_qrtr_info)
        for report in reports:
            report.xmlNumFile = xml_file
        return reports

    db_manager.find_reports_before_quarter = mock_find_reports

    # Create housekeeper with start quarter 2023q1
    housekeeper = Housekeeper(
        start_qrtr_info=QuarterInfo(year=2023, qrtr=1),
        xml_dir=test_dirs["xml_dir"],
        csv_dir=test_dirs["csv_dir"],
        secstyle_dir=test_dirs["secstyle_dir"],
        daily_zip_dir=test_dirs["daily_zip_dir"],
        quarter_zip_dir=test_dirs["quarter_zip_dir"],
        db_manager=db_manager,
    )

    # Run process with all options
    result = housekeeper.process(
        remove_processing_files=True, remove_db_entries=True, remove_quarter_zip_files=True, remove_daily_zip_files=True
    )

    # Check results
    assert result["processing_files_removed"] == 1
    assert result["db_entries_removed"] == 1
    assert result["quarter_zip_files_removed"] == 1
    assert result["daily_zip_files_removed"] == 1

    # Check that files were removed
    assert not os.path.exists(xml_file)
    assert not os.path.exists(quarter_zip)
    assert not os.path.exists(daily_zip)
    assert not os.path.exists(daily_zip_dir)

    # Verify database state
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sec_reports WHERE filingYear = 2022")
    assert cursor.fetchone()[0] == 0
    conn.close()
