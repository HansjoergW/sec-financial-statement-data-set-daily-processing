"""
Core definitions module containing constants, data types, and utility classes used throughout the application.
Provides quarter-related functionality, data type definitions, and the QuarterInfo class.
"""

import logging
from datetime import datetime
from typing import Optional

from numpy import float64, int64

MONTH_TO_QRTR = {1: 1, 2: 1, 3: 1, 4: 2, 5: 2, 6: 2, 7: 3, 8: 3, 9: 3, 10: 4, 11: 4, 12: 4}
QRTR_TO_MONTHS = {1: [1, 2, 3], 2: [4, 5, 6], 3: [7, 8, 9], 4: [10, 11, 12]}

DTYPES_NUM = {
    "adsh": str,
    "tag": str,
    "version": str,
    "ddate": int64,
    "qtrs": int,
    "uom": str,
    "coreg": str,
    "value": float64,
    "footnote": str,
    "segments": str,
}

DTYPES_PRE = {
    "adsh": str,
    "stmt": str,
    "tag": str,
    "version": str,
    "line": int,
    "report": int,
    "negating": int,
    "plabel": str,
}

DTYPES_LAB = {"key": str, "label": str, "to_entry": str}


class QuarterInfo:

    def __init__(self, year: Optional[int] = None, qrtr: Optional[int] = None):
        self.year: int
        self.qrtr: int

        today = datetime.today()
        if year is None:
            self.year = today.year
            if qrtr is not None:
                logging.info("set 'qrtr' is ignored, since 'year' is not set")

            self.qrtr = MONTH_TO_QRTR[today.month]
        else:
            self.year = year
            if qrtr is None:
                self.qrtr = 1
            else:
                self.qrtr = qrtr

        self.qrtr_string = get_qrtr_string(self.year, self.qrtr)
        self.qrtr_value: int = qrtr_value(self.year, self.qrtr)


def qrtr_value(year: int, qrtr: int) -> int:
    return year * 10 + qrtr


def qrtr_value_from_string(qrtr_string: str) -> int:
    "qrtr_string is in format 'YYYYqQ'"

    if not (len(qrtr_string) == 6 and qrtr_string[4] == "q" and qrtr_string[:4].isdigit() and qrtr_string[5].isdigit()):
        raise ValueError(f"Invalid quarter string format: {qrtr_string}")

    year = int(qrtr_string[:-2])
    qrtr = int(qrtr_string[-1])
    return qrtr_value(year, qrtr)


def get_qrtr_string_by_month(year: int, month: int) -> str:
    return get_qrtr_string(year, MONTH_TO_QRTR[month])


def get_qrtr_string(year: int, qrtr: int) -> str:
    return str(year) + "q" + str(qrtr)
