from datetime import datetime
from unittest.mock import patch

from numpy import float64, int64

from secdaily._00_common.BaseDefinitions import (
    DTYPES_LAB,
    DTYPES_NUM,
    DTYPES_PRE,
    MONTH_TO_QRTR,
    QRTR_TO_MONTHS,
    QuarterInfo,
    get_qrtr_string,
    get_qrtr_string_by_month,
)


class TestConstants:
    """Tests for the constant definitions in BaseDefinitions."""

    def test_month_to_qrtr_mapping(self):
        """Test that MONTH_TO_QRTR maps months to the correct quarters."""
        # Q1: January, February, March
        assert MONTH_TO_QRTR[1] == 1
        assert MONTH_TO_QRTR[2] == 1
        assert MONTH_TO_QRTR[3] == 1

        # Q2: April, May, June
        assert MONTH_TO_QRTR[4] == 2
        assert MONTH_TO_QRTR[5] == 2
        assert MONTH_TO_QRTR[6] == 2

        # Q3: July, August, September
        assert MONTH_TO_QRTR[7] == 3
        assert MONTH_TO_QRTR[8] == 3
        assert MONTH_TO_QRTR[9] == 3

        # Q4: October, November, December
        assert MONTH_TO_QRTR[10] == 4
        assert MONTH_TO_QRTR[11] == 4
        assert MONTH_TO_QRTR[12] == 4

    def test_qrtr_to_months_mapping(self):
        """Test that QRTR_TO_MONTHS maps quarters to the correct months."""
        assert QRTR_TO_MONTHS[1] == [1, 2, 3]  # Q1: January, February, March
        assert QRTR_TO_MONTHS[2] == [4, 5, 6]  # Q2: April, May, June
        assert QRTR_TO_MONTHS[3] == [7, 8, 9]  # Q3: July, August, September
        assert QRTR_TO_MONTHS[4] == [10, 11, 12]  # Q4: October, November, December

    def test_dtypes_num(self):
        """Test that DTYPES_NUM contains the expected column types."""
        assert DTYPES_NUM["adsh"] is str
        assert DTYPES_NUM["tag"] is str
        assert DTYPES_NUM["version"] is str
        assert DTYPES_NUM["ddate"] is int64
        assert DTYPES_NUM["qtrs"] is int
        assert DTYPES_NUM["uom"] is str
        assert DTYPES_NUM["coreg"] is str
        assert DTYPES_NUM["value"] is float64
        assert DTYPES_NUM["footnote"] is str
        assert DTYPES_NUM["segments"] is str

    def test_dtypes_pre(self):
        """Test that DTYPES_PRE contains the expected column types."""
        assert DTYPES_PRE["adsh"] is str
        assert DTYPES_PRE["stmt"] is str
        assert DTYPES_PRE["tag"] is str
        assert DTYPES_PRE["version"] is str
        assert DTYPES_PRE["line"] is int
        assert DTYPES_PRE["report"] is int
        assert DTYPES_PRE["negating"] is int
        assert DTYPES_PRE["plabel"] is str

    def test_dtypes_lab(self):
        """Test that DTYPES_LAB contains the expected column types."""
        assert DTYPES_LAB["key"] is str
        assert DTYPES_LAB["label"] is str
        assert DTYPES_LAB["to_entry"] is str


class TestQuarterInfo:
    """Tests for the QuarterInfo class."""

    def test_init_with_all_parameters(self):
        """Test initialization with all parameters provided."""
        quarter_info = QuarterInfo(year=2023, qrtr=2)

        assert quarter_info.year == 2023
        assert quarter_info.qrtr == 2
        assert quarter_info.qrtr_string == "2023q2"

    def test_init_with_year_and_qrtr(self):
        """Test initialization with year and quarter provided."""
        quarter_info = QuarterInfo(year=2023, qrtr=2)

        assert quarter_info.year == 2023
        assert quarter_info.qrtr == 2
        assert quarter_info.qrtr_string == "2023q2"

    def test_init_with_year_only(self):
        """Test initialization with only year provided."""
        quarter_info = QuarterInfo(year=2023)

        assert quarter_info.year == 2023
        assert quarter_info.qrtr == 1  # Default to Q1
        assert quarter_info.qrtr_string == "2023q1"

    @patch("secdaily._00_common.BaseDefinitions.datetime")
    def test_init_with_no_parameters(self, mock_datetime):
        """Test initialization with no parameters provided."""
        # Mock datetime.today() to return a fixed date
        mock_date = datetime(2023, 5, 15)  # May 15, 2023 (Q2)
        mock_datetime.today.return_value = mock_date

        quarter_info = QuarterInfo()

        assert quarter_info.year == 2023
        assert quarter_info.qrtr == 2  # Q2 for May
        assert quarter_info.qrtr_string == "2023q2"

    @patch("secdaily._00_common.BaseDefinitions.datetime")
    def test_init_with_qrtr_only(self, mock_datetime):
        """Test initialization with only quarter provided."""
        # Mock datetime.today() to return a fixed date
        mock_date = datetime(2023, 5, 15)  # May 15, 2023
        mock_datetime.today.return_value = mock_date

        # When only qrtr is provided but year is not, qrtr should be ignored
        quarter_info = QuarterInfo(qrtr=3)

        assert quarter_info.year == 2023  # From mocked current date
        assert quarter_info.qrtr == 2  # From mocked current date (Q2 for May)
        assert quarter_info.qrtr_string == "2023q2"

    @patch("secdaily._00_common.BaseDefinitions.logging")
    @patch("secdaily._00_common.BaseDefinitions.datetime")
    def test_init_with_qrtr_only_logs_warning(self, mock_datetime, mock_logging):
        """Test that a warning is logged when only quarter is provided."""
        # Mock datetime.today() to return a fixed date
        mock_date = datetime(2023, 5, 15)  # May 15, 2023
        mock_datetime.today.return_value = mock_date

        QuarterInfo(qrtr=3)

        # Check that a warning was logged
        mock_logging.info.assert_called_once_with("set 'qrtr' is ignored, since 'year' is not set")


class TestUtilityFunctions:
    """Tests for the utility functions in BaseDefinitions."""

    def test_get_qrtr_string(self):
        """Test the get_qrtr_string function."""
        assert get_qrtr_string(2023, 1) == "2023q1"
        assert get_qrtr_string(2023, 2) == "2023q2"
        assert get_qrtr_string(2023, 3) == "2023q3"
        assert get_qrtr_string(2023, 4) == "2023q4"
        assert get_qrtr_string(2022, 4) == "2022q4"

    def test_get_qrtr_string_by_month(self):
        """Test the get_qrtr_string_by_month function."""
        # Q1: January, February, March
        assert get_qrtr_string_by_month(2023, 1) == "2023q1"
        assert get_qrtr_string_by_month(2023, 2) == "2023q1"
        assert get_qrtr_string_by_month(2023, 3) == "2023q1"

        # Q2: April, May, June
        assert get_qrtr_string_by_month(2023, 4) == "2023q2"
        assert get_qrtr_string_by_month(2023, 5) == "2023q2"
        assert get_qrtr_string_by_month(2023, 6) == "2023q2"

        # Q3: July, August, September
        assert get_qrtr_string_by_month(2023, 7) == "2023q3"
        assert get_qrtr_string_by_month(2023, 8) == "2023q3"
        assert get_qrtr_string_by_month(2023, 9) == "2023q3"

        # Q4: October, November, December
        assert get_qrtr_string_by_month(2023, 10) == "2023q4"
        assert get_qrtr_string_by_month(2023, 11) == "2023q4"
        assert get_qrtr_string_by_month(2023, 12) == "2023q4"

        # Different year
        assert get_qrtr_string_by_month(2022, 12) == "2022q4"
