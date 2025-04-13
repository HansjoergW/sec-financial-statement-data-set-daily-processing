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


def get_qrtr_string_by_month(year: int, month: int) -> str:
    return get_qrtr_string(year, MONTH_TO_QRTR[month])


def get_qrtr_string(year: int, qrtr: int) -> str:
    return str(year) + "q" + str(qrtr)
