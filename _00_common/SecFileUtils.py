import requests
import logging
from time import sleep

def download_url_to_file(file_url:str, target_file:str):

    response = None
    current_try = 0
    while current_try < 4:
        current_try += 1
        try:
            response = requests.get(file_url, timeout=10)
            response.raise_for_status()
            break
        except requests.exceptions.RequestException as err:
            if current_try >= 4:
                logging.exception("RequestException:%s", err)
                raise err
            else:
                logging.info("failed try " + str(current_try))
                sleep(1)


    with open(target_file, 'w') as file:
        file.write(response.text)