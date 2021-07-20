import requests
import logging
from time import sleep
from pathlib import Path
import os
import pandas as pd
import zipfile

# downloads the content of a url and stores it into a file
# tries to download the file multiple times, if the download fails
def download_url_to_file(file_url:str, target_file:str, expected_size: int = None):

    content = get_url_content(file_url)
    if expected_size != None:
        if len(content) != expected_size:
            logging.info(f"warning expected size {expected_size} - real size {len(content)}")
            # raise Exception("wrong length downloaded")

    # with io.open(target_file, 'w', newline="\n") as file:
    #     file.write(content)
    write_content_to_zip(content, target_file)


def get_url_content(file_url:str) -> str:
    max_tries = 6

    response = None
    current_try = 0
    while current_try < max_tries:
        current_try += 1
        try:
            response = requests.get(file_url, timeout=10)
            response.raise_for_status()
            break
        except requests.exceptions.RequestException as err:
            if current_try >= max_tries:
                logging.info(f"RequestException: failed to download {file_url}")
                raise err
            else:
                sleep(1)

    return response.text


def _check_if_zipped(path: str) -> bool:
    return os.path.isfile(path + ".zip")


def write_df_to_zip(df:pd.DataFrame, filename:str):
    csv_content = df.to_csv(sep='\t', header=True)
    write_content_to_zip(csv_content, filename)


def read_df_from_zip(filename:str) -> pd.DataFrame:
    if _check_if_zipped(filename):
        with zipfile.ZipFile(filename + ".zip", "r") as zf:
            file = Path(filename).name
            return pd.read_csv(zf.open(file), header=0, delimiter="\t")
    else:
        return pd.read_csv(filename, header=0, delimiter="\t")


def write_content_to_zip(content:str, filename:str):
    with zipfile.ZipFile(filename + ".zip", mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        file = Path(filename).name
        zf.writestr(file, content)


def read_content_from_zip(filename:str) -> str:
    if _check_if_zipped(filename):
        with zipfile.ZipFile(filename + ".zip", mode="r") as zf:
            file = Path(filename).name
            return zf.read(file).decode("utf-8")
    else:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()