import requests
import logging

import re
# listet alle filenamen sauber
xml_file = re.compile(r"\"name\":\"(.*?)\"", re.IGNORECASE + re.MULTILINE + re.DOTALL)

testfile ="https://www.sec.gov/Archives/edgar/data/861459/000143774921004124/index.json"

response = None
try:
    response = requests.get(testfile, timeout=4)
    response.raise_for_status()
except requests.exceptions.RequestException as err:
    logging.exception("RequestException:%s", err)

print(response.text)

marks  = xml_file.finditer(response.text)
for mark in marks:
    if mark.groups()[0].endswith("htm.xml"):
        print(mark.groups()[0])
        try:
            response = requests.get("https://www.sec.gov/Archives/edgar/data/861459/000143774921004124/" + mark.groups()[0], timeout=4)
            response.raise_for_status()
            print(response.text[0:1000])
        except requests.exceptions.RequestException as err:
            logging.exception("RequestException:%s", err)
