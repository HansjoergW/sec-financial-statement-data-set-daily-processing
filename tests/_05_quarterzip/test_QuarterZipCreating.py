import os
import shutil
import tempfile
import zipfile

import pandas as pd
import pytest

from secdaily._00_common.BaseDefinitions import QuarterInfo
from secdaily._05_quarterzip.QuarterZipCreating import QuarterZipCreator


@pytest.fixture
def test_dirs():
    """Create temporary directories for testing."""
    temp_dir = tempfile.mkdtemp()
    daily_dir = os.path.join(temp_dir, "daily")
    quarter_dir = os.path.join(temp_dir, "quarter")

    os.makedirs(daily_dir, exist_ok=True)
    os.makedirs(quarter_dir, exist_ok=True)

    yield daily_dir, quarter_dir

    # Cleanup
    shutil.rmtree(temp_dir)


def create_test_daily_zip(daily_dir, year, qrtr, day, adsh_list):
    """Create a test daily zip file with sample data."""
    qrtr_str = f"{year}q{qrtr}"
    qrtr_dir = os.path.join(daily_dir, qrtr_str)
    os.makedirs(qrtr_dir, exist_ok=True)

    # Format day as two digits
    day_str = f"{day:02d}"
    month_str = "01" if qrtr == 1 else "04" if qrtr == 2 else "07" if qrtr == 3 else "10"

    # Create sample DataFrames
    sub_data = []
    pre_data = []
    num_data = []

    for adsh in adsh_list:
        # Add sub data
        sub_data.append(
            {
                "adsh": adsh,
                "cik": f"000{adsh[-5:]}",
                "name": f"Company {adsh[-5:]}",
                "form": "10-K",
                "period": f"{year}0101",
                "fy": year,
                "fp": "FY",
                "filed": f"{year}{month_str}{day_str}",
            }
        )

        # Add pre data
        for i in range(3):
            pre_data.append(
                {
                    "adsh": adsh,
                    "stmt": "BS",
                    "tag": f"tag{i}",
                    "version": "us-gaap/2020",
                    "line": i + 1,
                    "report": 1,
                    "negating": 0,
                    "plabel": f"Label {i}",
                }
            )

        # Add num data
        for i in range(3):
            num_data.append(
                {
                    "adsh": adsh,
                    "tag": f"tag{i}",
                    "version": "us-gaap/2020",
                    "ddate": int(f"{year}0101"),
                    "qtrs": 4,
                    "uom": "USD",
                    "coreg": "",
                    "value": 1000.0 * (i + 1),
                    "footnote": "",
                    "segments": "",
                }
            )

    # Create DataFrames
    sub_df = pd.DataFrame(sub_data)
    pre_df = pd.DataFrame(pre_data)
    num_df = pd.DataFrame(num_data)

    # Create zip file
    zip_path = os.path.join(qrtr_dir, f"{year}{month_str}{day_str}.zip")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("sub.txt", sub_df.to_csv(sep="\t", header=True, index=False))
        zf.writestr("pre.txt", pre_df.to_csv(sep="\t", header=True, index=False))
        zf.writestr("num.txt", num_df.to_csv(sep="\t", header=True, index=False))

    return zip_path


def test_create_quarter_zip_new(test_dirs):
    """Test creating a new quarter zip file."""
    daily_dir, quarter_dir = test_dirs

    # Create test daily zip files
    year = 2024
    qrtr = 1
    qrtr_info = QuarterInfo(year=year, qrtr=qrtr)

    # Create 3 daily zip files with different ADSHs
    create_test_daily_zip(daily_dir, year, qrtr, 1, ["0001234567-24-000001", "0001234567-24-000002"])
    create_test_daily_zip(daily_dir, year, qrtr, 2, ["0001234567-24-000003", "0001234567-24-000004"])
    create_test_daily_zip(daily_dir, year, qrtr, 3, ["0001234567-24-000005", "0001234567-24-000006"])

    # Create QuarterZipCreator and process the quarter
    creator = QuarterZipCreator(start_qrtr_info=qrtr_info, daily_zip_dir=daily_dir, quarter_zip_dir=quarter_dir)
    result = creator.process_quarter(qrtr_info)

    # Check that the quarter zip was created
    assert result is True
    quarter_zip_path = os.path.join(quarter_dir, f"{year}q{qrtr}.zip")
    assert os.path.exists(quarter_zip_path)

    # Check the contents of the quarter zip
    with zipfile.ZipFile(quarter_zip_path, "r") as zf:
        # Check that the expected files are in the zip
        assert "sub.txt" in zf.namelist()
        assert "pre.txt" in zf.namelist()
        assert "num.txt" in zf.namelist()
        assert "metadata.txt" in zf.namelist()

        # Check that the metadata contains the daily zip filenames
        metadata = zf.read("metadata.txt").decode("utf-8")
        assert "20240101.zip" in metadata
        assert "20240102.zip" in metadata
        assert "20240103.zip" in metadata

        # Check that the sub.txt contains all ADSHs
        with zf.open("sub.txt") as f:
            sub_df = pd.read_csv(f, sep="\t", header=0)
        assert len(sub_df) == 6  # 2 ADSHs per day, 3 days

        # Check that the pre.txt contains all entries
        with zf.open("pre.txt") as f:
            pre_df = pd.read_csv(f, sep="\t", header=0)
        assert len(pre_df) == 18  # 3 entries per ADSH, 6 ADSHs

        # Check that the num.txt contains all entries
        with zf.open("num.txt") as f:
            num_df = pd.read_csv(f, sep="\t", header=0)
        assert len(num_df) == 18  # 3 entries per ADSH, 6 ADSHs


def test_update_quarter_zip(test_dirs):
    """Test updating an existing quarter zip file with new daily zip files."""
    daily_dir, quarter_dir = test_dirs

    # Create test daily zip files
    year = 2024
    qrtr = 1
    qrtr_info = QuarterInfo(year=year, qrtr=qrtr)

    # Create initial daily zip files
    create_test_daily_zip(daily_dir, year, qrtr, 1, ["0001234567-24-000001", "0001234567-24-000002"])
    create_test_daily_zip(daily_dir, year, qrtr, 2, ["0001234567-24-000003", "0001234567-24-000004"])

    # Create QuarterZipCreator and process the quarter
    creator = QuarterZipCreator(start_qrtr_info=qrtr_info, daily_zip_dir=daily_dir, quarter_zip_dir=quarter_dir)
    creator.process_quarter(qrtr_info)

    # Create a new daily zip file
    create_test_daily_zip(daily_dir, year, qrtr, 3, ["0001234567-24-000005", "0001234567-24-000006"])

    # Process the quarter again
    result = creator.process_quarter(qrtr_info)

    # Check that the quarter zip was updated
    assert result is True
    quarter_zip_path = os.path.join(quarter_dir, f"{year}q{qrtr}.zip")

    # Check the contents of the updated quarter zip
    with zipfile.ZipFile(quarter_zip_path, "r") as zf:
        # Check that the metadata contains all daily zip filenames
        metadata = zf.read("metadata.txt").decode("utf-8")
        assert "20240101.zip" in metadata
        assert "20240102.zip" in metadata
        assert "20240103.zip" in metadata

        # Check that the sub.txt contains all ADSHs
        with zf.open("sub.txt") as f:
            sub_df = pd.read_csv(f, sep="\t", header=0)
        assert len(sub_df) == 6  # 2 ADSHs per day, 3 days

        # Check that all ADSHs are present
        adsh_list = sub_df["adsh"].tolist()
        for i in range(1, 7):
            assert f"0001234567-24-00000{i}" in adsh_list


def test_no_new_daily_files(test_dirs):
    """Test processing a quarter with no new daily zip files."""
    daily_dir, quarter_dir = test_dirs

    # Create test daily zip files
    year = 2024
    qrtr = 1
    qrtr_info = QuarterInfo(year=year, qrtr=qrtr)

    # Create daily zip files
    create_test_daily_zip(daily_dir, year, qrtr, 1, ["0001234567-24-000001", "0001234567-24-000002"])

    # Create QuarterZipCreator and process the quarter
    creator = QuarterZipCreator(start_qrtr_info=qrtr_info, daily_zip_dir=daily_dir, quarter_zip_dir=quarter_dir)
    creator.process_quarter(qrtr_info)

    # Get the modification time of the quarter zip
    quarter_zip_path = os.path.join(quarter_dir, f"{year}q{qrtr}.zip")
    mtime_before = os.path.getmtime(quarter_zip_path)

    # Process the quarter again without adding new daily zip files
    result = creator.process_quarter(qrtr_info)

    # Check that the quarter zip was not modified
    assert result is True
    mtime_after = os.path.getmtime(quarter_zip_path)
    assert mtime_before == mtime_after


def test_no_daily_files(test_dirs):
    """Test processing a quarter with no daily zip files."""
    daily_dir, quarter_dir = test_dirs

    # Create QuarterZipCreator and process a quarter with no daily zip files
    qrtr_info = QuarterInfo(year=2024, qrtr=1)
    creator = QuarterZipCreator(start_qrtr_info=qrtr_info, daily_zip_dir=daily_dir, quarter_zip_dir=quarter_dir)
    result = creator.process_quarter(qrtr_info)

    # Check that no quarter zip was created
    assert result is True  # Not an error, just nothing to do
    quarter_zip_path = os.path.join(quarter_dir, "2024q1.zip")
    assert not os.path.exists(quarter_zip_path)


def test_process_all_quarters(test_dirs):
    """Test processing all quarters."""
    daily_dir, quarter_dir = test_dirs

    # Create test daily zip files for multiple quarters
    create_test_daily_zip(daily_dir, 2024, 1, 1, ["0001234567-24-000001"])
    create_test_daily_zip(daily_dir, 2024, 2, 1, ["0001234567-24-000002"])

    # Create QuarterZipCreator and process all quarters
    start_qrtr_info = QuarterInfo(year=2024, qrtr=1)
    creator = QuarterZipCreator(start_qrtr_info=start_qrtr_info, daily_zip_dir=daily_dir, quarter_zip_dir=quarter_dir)
    creator.process()

    # Check that quarter zips were created for both quarters
    assert os.path.exists(os.path.join(quarter_dir, "2024q1.zip"))
    assert os.path.exists(os.path.join(quarter_dir, "2024q2.zip"))


def test_process_with_start_quarter_filter(test_dirs):
    """Test that only quarters equal or later than start_qrtr_info are processed."""
    daily_dir, quarter_dir = test_dirs

    # Create test daily zip files for multiple quarters
    create_test_daily_zip(daily_dir, 2023, 4, 1, ["0001234567-23-000001"])  # 2023Q4 - should be skipped
    create_test_daily_zip(daily_dir, 2024, 1, 1, ["0001234567-24-000001"])  # 2024Q1 - should be processed
    create_test_daily_zip(daily_dir, 2024, 2, 1, ["0001234567-24-000002"])  # 2024Q2 - should be processed

    # Create QuarterZipCreator with start quarter of 2024Q1
    start_qrtr_info = QuarterInfo(year=2024, qrtr=1)
    creator = QuarterZipCreator(start_qrtr_info=start_qrtr_info, daily_zip_dir=daily_dir, quarter_zip_dir=quarter_dir)
    creator.process()

    # Check that only quarter zips for 2024Q1 and later were created
    assert not os.path.exists(os.path.join(quarter_dir, "2023q4.zip"))  # Should not exist
    assert os.path.exists(os.path.join(quarter_dir, "2024q1.zip"))  # Should exist
    assert os.path.exists(os.path.join(quarter_dir, "2024q2.zip"))  # Should exist
