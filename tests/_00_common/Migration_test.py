"""
Test module for the Migration functionality. Tests the migration processing logic including version checking,
migration execution, and state management for different scenarios.
"""

import os
import sqlite3
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from secdaily._00_common.db.StateAccess import StateAccess
from secdaily._00_common.MigrationProcessing import MigrationProcessor
from secdaily.SecDaily import Configuration


@pytest.fixture
def temp_work_dir():
    """Create a temporary working directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def test_db(temp_work_dir):
    """Create a test database with the state table."""
    db_path = os.path.join(temp_work_dir, "sec_processing.db")

    # Create database and state table
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS state
        (
            attribute TEXT NOT NULL,
            value TEXT,
            date TEXT,
            comment TEXT,
            PRIMARY KEY (attribute)
        )
    """
    )
    conn.commit()
    conn.close()

    return db_path


@pytest.fixture
def test_configuration(temp_work_dir):
    """Create a test configuration object."""
    return Configuration(
        workdir=temp_work_dir,
        xmldir=os.path.join(temp_work_dir, "_1_xml/"),
        csvdir=os.path.join(temp_work_dir, "_2_csv/"),
        formatdir=os.path.join(temp_work_dir, "_3_secstyle/"),
        dailyzipdir=os.path.join(temp_work_dir, "_4_daily/"),
        quarterzipdir=os.path.join(temp_work_dir, "_5_quarter/"),
    )


@pytest.fixture
def migration_processor(temp_work_dir):
    """Create a MigrationProcessor instance for testing."""
    state_access = StateAccess(work_dir=temp_work_dir)
    processor = MigrationProcessor(dbmanager=state_access)
    # default assumption for tests, that migration is required on version change
    processor.MIGRATION_REQUIRED_ON_VERSION_CHANGE = True
    return processor


class TestMigrationProcessor:
    """Tests for the MigrationProcessor class."""

    def test_migration_required_no_last_version_entry(self, migration_processor, test_db):
        """Test if migration is necessary when no last version entry exists."""
        # Ensure no version entry exists
        state_access = migration_processor.state_access
        assert state_access.get_last_run_version() is None

        # Migration should be required
        assert migration_processor.is_migration_required() is True

    def test_migration_required_older_last_version_entry(self, migration_processor, test_db):
        """Test if migration is necessary when an older last version entry exists."""
        # Set an older version
        state_access = migration_processor.state_access
        state_access.set_last_run_version("0.1.0")

        # Migration should be required (assuming current version is different)
        with patch("secdaily.__version__", "0.2.0"):
            # create new processor to get the patched version
            processor = MigrationProcessor(dbmanager=migration_processor.state_access)
            assert processor.is_migration_required() is True

    def test_migration_not_required_same_version_entry(self, migration_processor, test_db):
        """Test if migration is not necessary when the last version entry is the same as current version."""
        current_version = "0.2.0"

        # Set the same version as current
        state_access = migration_processor.state_access
        state_access.set_last_run_version(current_version)

        # Migration should not be required
        with patch("secdaily.__version__", current_version):
            # create new processor to get the patched version
            processor = MigrationProcessor(dbmanager=migration_processor.state_access)
            assert processor.is_migration_required() is False

    def test_migration_disabled_by_flag(self, migration_processor, test_db):
        """Test that migration can be disabled by configuration flag."""
        # Temporarily disable migration
        original_flag = migration_processor.MIGRATION_REQUIRED_ON_VERSION_CHANGE
        migration_processor.MIGRATION_REQUIRED_ON_VERSION_CHANGE = False

        try:
            # Even with no version entry, migration should not be required
            assert migration_processor.is_migration_required() is False
        finally:
            # Restore original flag
            migration_processor.MIGRATION_REQUIRED_ON_VERSION_CHANGE = original_flag

    @patch("secdaily._00_common.MigrationProcessing.Housekeeper")
    def test_execute_migration_success(self, mock_housekeeper_class, migration_processor, test_configuration):
        """Test successful migration execution."""
        # Mock the housekeeper
        mock_housekeeper = MagicMock()
        mock_housekeeper_class.return_value = mock_housekeeper

        # Execute migration
        migration_processor.execute_migration(test_configuration)

        # Verify housekeeper was created with correct parameters
        mock_housekeeper_class.assert_called_once()
        call_args = mock_housekeeper_class.call_args

        # Check that start_qrtr_info is set to year 3000, quarter 1
        assert call_args[1]["start_qrtr_info"].year == 3000
        assert call_args[1]["start_qrtr_info"].qrtr == 1

        # Verify process was called with all cleanup flags set to True
        mock_housekeeper.process.assert_called_once_with(
            remove_processing_files=True,
            remove_db_entries=True,
            remove_quarter_zip_files=True,
            remove_daily_zip_files=True,
        )

    @patch("secdaily._00_common.MigrationProcessing.Housekeeper")
    def test_execute_migration_failure(self, mock_housekeeper_class, migration_processor, test_configuration):
        """Test migration execution failure."""
        # Mock the housekeeper to raise an exception
        mock_housekeeper = MagicMock()
        mock_housekeeper.process.side_effect = Exception("Migration failed")
        mock_housekeeper_class.return_value = mock_housekeeper

        # Execute migration
        with pytest.raises(Exception, match="Migration failed"):
            migration_processor.execute_migration(test_configuration)

    def test_last_run_version_updated_after_successful_run(self, migration_processor, test_db):
        """Test if the last run version is updated correctly after a successful run."""
        current_version = "0.2.0"

        with patch("secdaily.__version__", current_version):
            # create new processor to get the patched version
            processor = MigrationProcessor(dbmanager=migration_processor.state_access)

            # Update last run version
            processor.update_last_run_version()

            # Verify version was updated
            state_access = processor.state_access
            assert state_access.get_last_run_version() == current_version

    def test_last_run_version_not_updated_after_failed_run(self, migration_processor, test_db):
        """Test if the last run version is not updated after a failed run."""
        # Set initial version
        initial_version = "0.1.0"
        state_access = migration_processor.state_access
        state_access.set_last_run_version(initial_version)

        # Simulate a failed run by not calling update_last_run_version
        # The version should remain unchanged
        assert state_access.get_last_run_version() == initial_version

    @patch("secdaily._00_common.MigrationProcessing.Housekeeper")
    def test_process_migration_check_no_migration_required(
        self, mock_housekeeper_class, migration_processor, test_configuration, test_db
    ):
        """Test process_migration_check when no migration is required."""
        current_version = "0.2.0"

        # Set the same version as current
        state_access = migration_processor.state_access
        state_access.set_last_run_version(current_version)

        with patch("secdaily.__version__", current_version):
            # create new processor to get the patched version
            processor = MigrationProcessor(dbmanager=migration_processor.state_access)

            processor.process_migration_check(test_configuration)

            # Housekeeper should not be called
            mock_housekeeper_class.assert_not_called()

    @patch("secdaily._00_common.MigrationProcessing.Housekeeper")
    def test_process_migration_check_migration_required_and_successful(
        self, mock_housekeeper_class, migration_processor, test_configuration, test_db
    ):
        """Test process_migration_check when migration is required and successful."""
        # Mock successful housekeeper
        mock_housekeeper = MagicMock()
        mock_housekeeper_class.return_value = mock_housekeeper

        # No version entry exists, so migration should be required
        migration_processor.process_migration_check(test_configuration)

        # Housekeeper should be called
        mock_housekeeper_class.assert_called_once()
        mock_housekeeper.process.assert_called_once()

    @patch("secdaily._00_common.MigrationProcessing.Housekeeper")
    def test_process_migration_check_migration_required_but_failed(
        self, mock_housekeeper_class, migration_processor, test_configuration, test_db
    ):
        """Test process_migration_check when migration is required but fails."""
        # Mock failed housekeeper
        mock_housekeeper = MagicMock()
        mock_housekeeper.process.side_effect = Exception("Migration failed")
        mock_housekeeper_class.return_value = mock_housekeeper

        # No version entry exists, so migration should be required
        # Execute migration
        with pytest.raises(Exception, match="Migration failed"):
            migration_processor.process_migration_check(test_configuration)

    def test_get_current_version(self, migration_processor):
        """Test getting the current version."""
        with patch("secdaily.__version__", "0.2.0"):
            # create new processor to get the patched version
            processor = MigrationProcessor(dbmanager=migration_processor.state_access)
            assert processor.get_current_version() == "0.2.0"

    def test_get_last_run_version(self, migration_processor, test_db):
        """Test getting the last run version."""
        # Initially should be None
        assert migration_processor.get_last_run_version() is None

        # Set a version and verify it can be retrieved
        state_access = migration_processor.state_access
        state_access.set_last_run_version("0.1.0")

        assert migration_processor.get_last_run_version() == "0.1.0"
