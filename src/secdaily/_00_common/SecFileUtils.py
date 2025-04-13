import os
import zipfile
from pathlib import Path
from typing import Any, Optional

import pandas as pd


def _check_if_zipped(path: str) -> bool:
    return os.path.isfile(path + ".zip")


def write_df_to_zip(df: pd.DataFrame, filename: str):
    csv_content = df.to_csv(sep="\t", header=True, index=False)
    write_content_to_zip(csv_content, filename)


def read_df_from_zip(filename: str, dtype: Optional[Any] = None) -> pd.DataFrame:
    if _check_if_zipped(filename):
        with zipfile.ZipFile(filename + ".zip", "r") as zf:
            file = Path(filename).name
            return pd.read_csv(zf.open(file), header=0, delimiter="\t")
    else:
        return pd.read_csv(filename, header=0, delimiter="\t", dtype=dtype)


def read_file_from_zip(zip_file: str, filename: str, dtype: Optional[Any] = None) -> pd.DataFrame:
    with zipfile.ZipFile(zip_file, "r") as zf:
        file = Path(filename).name
        return pd.read_csv(zf.open(file), header=0, delimiter="\t", dtype=dtype)


def write_content_to_zip(content: str, filename: str):
    with zipfile.ZipFile(filename + ".zip", mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        file = Path(filename).name
        zf.writestr(file, content)


def read_content_from_zip(filename: str) -> str:
    if _check_if_zipped(filename):
        with zipfile.ZipFile(filename + ".zip", mode="r") as zf:
            file = Path(filename).name
            return zf.read(file).decode("utf-8")
    else:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
