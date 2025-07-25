"""
Migration processing module for handling version changes and data migration. Provides functionality to check
for version changes, execute migration scripts when necessary, and manage the migration process.
"""

import logging
from typing import Optional

import secdaily
from secdaily._00_common.BaseDefinitions import QuarterInfo
from secdaily._00_common.db.StateAccess import StateAccess
from secdaily._06_cleanup.Housekeeping import Housekeeper


class MigrationProcessor:
    """
    Handles migration processing for version changes.

    This class checks if the current version differs from the last run version
    and executes migration scripts when necessary. It provides a simple boolean
    flag to determine if migration is required.
    """

    # Boolean flag that defines whether a migration is necessary if the version has changed
    MIGRATION_REQUIRED_ON_VERSION_CHANGE: bool = True

    def __init__(self, dbmanager: StateAccess):
        """
        Initialize the MigrationProcessor.

        Args:
            dbmanager: Database manager for state access
        """
        self.state_access = dbmanager
        self.current_version = secdaily.__version__

    def is_migration_required(self) -> bool:
        """
        Check if migration is required based on version comparison.

        Returns:
            True if migration is required, False otherwise
        """
        if not self.MIGRATION_REQUIRED_ON_VERSION_CHANGE:
            logging.debug("Migration is disabled by configuration flag")
            return False

        last_run_version = self.state_access.get_last_run_version()

        if last_run_version is None:
            logging.info("No last run version found in state table - migration required")
            return True

        if (last_run_version != self.current_version) and not last_run_version == "0.0.0":
            logging.info(
                "Version change detected: last run version %s, current version %s - migration required",
                last_run_version,
                self.current_version,
            )
            return True

        logging.debug(
            "Version unchanged: current version %s matches last run version - no migration required",
            self.current_version,
        )
        return False

    def execute_migration(self, configuration):
        """
        Execute the migration process by removing all data using Housekeeping logic.

        Args:
            configuration: Configuration object containing directory paths

        """
        try:
            logging.info("Starting migration process - removing all data")

            # Use a very late start quarter (year 3000, quarter 1) to remove all data
            migration_start_quarter = QuarterInfo(year=3000, qrtr=1)

            # Create housekeeper with the configuration directories
            housekeeper = Housekeeper(
                start_qrtr_info=migration_start_quarter,
                xml_dir=configuration.xmldir,
                csv_dir=configuration.csvdir,
                secstyle_dir=configuration.formatdir,
                daily_zip_dir=configuration.dailyzipdir,
                quarter_zip_dir=configuration.quarterzipdir,
                work_dir=configuration.workdir,
            )

            # Execute complete cleanup
            housekeeper.process(
                remove_processing_files=True,
                remove_db_entries=True,
                remove_quarter_zip_files=True,
                remove_daily_zip_files=True,
            )

            logging.info("Migration completed successfully - all data removed")

        except Exception as e:  # pylint: disable=broad-except
            logging.error("Migration failed: %s.", e)
            logging.error("  Please clear all data manually and run the process again...")
            raise

    def process_migration_check(self, configuration):
        """
        Main method to check for migration requirements and execute if necessary.

        Args:
            configuration: Configuration object containing directory paths

        """
        logging.info("Starting migration check process")
        logging.info("Current version: %s", self.current_version)

        if not self.is_migration_required():
            logging.info("No migration required")
            return

        logging.info("Migration required - executing migration process")
        self.execute_migration(configuration)

        logging.info("Migration check process completed successfully")

    def update_last_run_version(self) -> None:
        """
        Update the last run version in the state table after a successful run.

        This should be called at the end of a successful processing run.
        """
        try:
            self.state_access.set_last_run_version(self.current_version)
            logging.info("Updated last run version to %s", self.current_version)
        except Exception as e:  # pylint: disable=broad-except
            logging.error("Failed to update last run version: %s", e)
            raise

    def get_current_version(self) -> str:
        """
        Get the current version of the application.

        Returns:
            Current version string
        """
        return self.current_version

    def get_last_run_version(self) -> Optional[str]:
        """
        Get the last run version from the state table.

        Returns:
            Last run version string, or None if not found
        """
        return self.state_access.get_last_run_version()
