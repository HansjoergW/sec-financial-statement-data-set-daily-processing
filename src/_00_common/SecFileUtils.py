import requests
import logging
from time import sleep
import io

# downloads the content of a url and stores it into a file
# tries to download the file multiple times, if the download fails
def download_url_to_file(file_url:str, target_file:str, expected_size: int = None):

    content = get_url_content(file_url)
    if expected_size != None:
        if len(content) != expected_size:
            raise Exception("wrong length downloaded")

    with io.open(target_file, 'w', newline="\n") as file:
        file.write(content)


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
                logging.exception("RequestException:%s", err)
                raise err
            else:
                logging.info("failed try " + str(current_try))
                sleep(1)

    return response.text
