"""
Data access module for state management. Provides database operations for storing and retrieving
application state information including version tracking and configuration attributes.
"""

import logging
from datetime import datetime
from typing import Optional

from secdaily._00_common.DBBase import DB


class StateAccess(DB):
    """
    Data access class for managing application state in the database.

    Provides methods to store and retrieve state information such as version tracking,
    configuration settings, and other persistent application attributes.
    """

    LAST_RUN_VERSION_ATTRIBUTE = "LAST_RUN_VERSION"

    def get_attribute(self, attribute: str) -> Optional[str]:
        """
        Get the value of a state attribute.

        Args:
            attribute: The name of the attribute to retrieve

        Returns:
            The value of the attribute, or None if not found
        """
        sql = f"""SELECT value FROM {DB.STATE_TBL_NAME} WHERE attribute = ?"""

        try:
            result = self._execute_fetchall_with_params(sql, (attribute,))
            return result[0][0] if result else None
        except Exception as e:  # pylint: disable=broad-except
            logging.error("Error retrieving attribute %s: %s", attribute, e)
            return None

    def set_attribute(self, attribute: str, value: str, comment: Optional[str] = None) -> None:
        """
        Set the value of a state attribute.

        Args:
            attribute: The name of the attribute to set
            value: The value to set
            comment: Optional comment describing the attribute
        """
        current_date = datetime.now().isoformat()

        # Use INSERT OR REPLACE to handle both insert and update cases
        sql = f"""INSERT OR REPLACE INTO {DB.STATE_TBL_NAME}
                  (attribute, value, date, comment)
                  VALUES (?, ?, ?, ?)"""

        try:
            self._execute_single_with_params(sql, (attribute, value, current_date, comment))
            logging.debug("Set attribute %s to value %s", attribute, value)
        except Exception as e:  # pylint: disable=broad-except
            logging.error("Error setting attribute %s: %s", attribute, e)
            raise

    def get_last_run_version(self) -> Optional[str]:
        """
        Get the version from the last successful run.

        Returns:
            The version string from the last run, or None if not found
        """
        return self.get_attribute(self.LAST_RUN_VERSION_ATTRIBUTE)

    def set_last_run_version(self, version: str) -> None:
        """
        Set the version for the last successful run.

        Args:
            version: The version string to store
        """
        comment = f"Version updated after successful run on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        self.set_attribute(self.LAST_RUN_VERSION_ATTRIBUTE, version, comment)

    def _execute_fetchall_with_params(self, sql: str, params: tuple):
        """Execute a SELECT query with parameters and return all results."""
        conn = self.get_connection()
        try:
            return conn.execute(sql, params).fetchall()
        finally:
            conn.close()

    def _execute_single_with_params(self, sql: str, params: tuple):
        """Execute a single SQL statement with parameters."""
        conn = self.get_connection()
        try:
            conn.execute(sql, params)
            conn.commit()
        finally:
            conn.close()
