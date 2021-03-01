from multiprocessing import Pool

import sqlite3 as sqlite3
import os
import re
import logging
import requests

# listet alle filenamen sauber
files = re.compile(r"\"name\":\"(.*?)\"", re.IGNORECASE + re.MULTILINE + re.DOTALL)

def _find_main_file(path:str):
    response = None
    json_file = path + "index.json"
    try:
        response = requests.get(json_file, timeout=4)
        response.raise_for_status()
    except requests.exceptions.RequestException as err:
        logging.exception("RequestException:%s", err)

    marks  = files.finditer(response.text)
    response.close()
    for mark in marks:
        if mark.groups()[0].endswith("htm.xml"):
            print("found for: " + path)
            return path + mark.groups()[0]
    return None


def f(mytuple):
    pre_url = mytuple[2]
    new_url = _find_main_file(pre_url[0:pre_url.rfind("/")+1])
    return new_url, mytuple[0]


if __name__ == '__main__':
    work_dir = "d:/edgar/"
    database = os.path.join(work_dir, 'edgar.db')

    conn = sqlite3.connect(database)
    result = conn.execute("SELECT accession_number, xbrl_files, xbrl_pre_url FROM feeds WHERE xbrl_files is NULL").fetchall()

    # limit sec: 10 requests per second
    pool = Pool(3)
    update_data = pool.map(f, result[:10])
    print(len(result))

    conn.executemany("UPDATE feeds SET xbrl_files = ? WHERE accession_number = ?", update_data)
    conn.commit()
    conn.close()



