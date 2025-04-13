import logging
from time import sleep
from typing import Optional

import requests

from secdaily._00_common.SecFileUtils import write_content_to_zip


class UrlDownloader:

    def __init__(self, user_agent: str = "<not set>"):
        """
        :param user_agent: according to https://www.sec.gov/os/accessing-edgar-data
         in the form User-Agent: Sample Company Name AdminContact@<sample company domain>.com
        """

        self.user_agent = user_agent

    # downloads the content of a url and stores it into a file
    # tries to download the file multiple times, if the download fails
    def download_url_to_file(
        self,
        file_url: str,
        target_file: str,
        expected_size: Optional[int] = None,
        max_tries: int = 6,
        sleep_time: int = 1,
    ):
        content = self.get_url_content(file_url, max_tries, sleep_time)
        if expected_size is not None:
            if len(content) != expected_size:
                logging.info("warning expected size %d - real size %d", expected_size, len(content))
                # raise Exception("wrong length downloaded")

        # with io.open(target_file, 'w', newline="\n") as file:
        #     file.write(content)
        write_content_to_zip(content, target_file)

    def get_url_content(self, file_url: str, max_tries: int = 6, sleep_time: int = 1) -> str:
        # preventing 403
        # https://stackoverflow.com/questions/68131406/downloading-files-from-sec-gov-via-edgar-using-python-3-9
        response = None
        current_try = 0
        while current_try < max_tries:
            current_try += 1
            try:
                response = requests.get(file_url, timeout=10, headers={"User-Agent": self.user_agent}, stream=True)
                response.raise_for_status()
                break
            except requests.exceptions.RequestException as err:
                if current_try >= max_tries:
                    logging.info("RequestException: failed to download %s", file_url)
                    raise err
                sleep(sleep_time)

        return response.text
