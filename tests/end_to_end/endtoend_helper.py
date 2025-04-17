#!/usr/bin/env python

import os
import shutil
import sqlite3
from sqlite3 import Error as SQLiteError

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))


def get_xml_files_for_adsh(adsh, sqlite_path):
    """
    Query the sec_report_processing table for XML file paths for a given ADSH.

    Args:
        adsh (str): The accession number to look up
        sqlite_path (str): Path to the SQLite database file

    Returns:
        tuple: (xmlNumFile, xmlPreFile, xmlLabFile) paths or None if not found
    """
    conn = sqlite3.connect(sqlite_path)
    try:
        cursor = conn.cursor()
        query = """SELECT xmlNumFile, xmlPreFile, xmlLabFile
                 FROM sec_report_processing
                 WHERE accessionNumber = ?"""
        cursor.execute(query, (adsh,))
        result = cursor.fetchone()
        return result
    except SQLiteError as e:
        print(f"Error querying database: {e}")
        return None
    finally:
        conn.close()


def copy_files_to_target(adsh, files, target_folder):
    """
    Copy XML files to a subfolder in the target folder.

    Args:
        adsh (str): The accession number (used as subfolder name)
        files (tuple): Tuple of (xmlNumFile, xmlPreFile, xmlLabFile) paths
        target_folder (str): Base target folder path

    Returns:
        bool: True if successful, False otherwise
    """
    if not all(files):
        print(f"Warning: Some files are missing for {adsh}")

    # Create subfolder named after the ADSH
    subfolder = os.path.join(target_folder, adsh)
    os.makedirs(subfolder, exist_ok=True)

    # Copy each file that exists
    success = True
    for file_path in files:
        if file_path:
            try:
                # Get just the filename from the path
                file_name = os.path.basename(file_path)
                # If the file is stored as a zip, handle that case
                if os.path.exists(file_path):
                    shutil.copy2(file_path, os.path.join(subfolder, file_name))
                elif os.path.exists(file_path + ".zip"):
                    shutil.copy2(file_path + ".zip", os.path.join(subfolder, file_name + ".zip"))
                else:
                    print(f"File not found: {file_path}")
                    success = False
            except (shutil.Error, OSError) as e:
                print(f"Error copying file {file_path}: {e}")
                success = False

    return success


def main(adsh, sqlite_path, target_folder):
    # Get the file paths from the database
    files = get_xml_files_for_adsh(adsh, sqlite_path)

    if not files:
        print(f"No files found for ADSH: {adsh}")
        return 1

    # Copy the files to the target folder
    success = copy_files_to_target(adsh, files, target_folder)

    if success:
        print(f"Successfully copied files for {adsh} to {os.path.join(target_folder, adsh)}")
        return 0

    print(f"Some files could not be copied for {adsh}")
    return 1


if __name__ == "__main__":
    main("0001477932-24-008123", "d:/secprocessing2/sec_processing.db", CURRENT_PATH + "/data")
    main("0000320193-24-000123", "d:/secprocessing2/sec_processing.db", CURRENT_PATH + "/data")
