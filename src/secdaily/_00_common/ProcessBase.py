import os
from pathlib import Path


class ProcessBase:

    def __init__(self, data_dir: str):
        self.data_dir = data_dir

        if self.data_dir[-1] != '/':
            self.data_dir = data_dir + '/'

        self.error_log_dir = self.data_dir + "error/"

        if not os.path.isdir(self.data_dir):
            os.makedirs(self.data_dir)

        if not os.path.isdir(self.error_log_dir):
            os.makedirs(self.error_log_dir)

        self.data_path = Path(self.data_dir)
        self.error_path = Path(self.error_log_dir)

    def _log_error(self, adsh: str, type: str, error: str):
        error_file_name = self.error_log_dir + type + "_" + adsh + ".txt"
        with open(error_file_name, "w", encoding="utf-8") as f:
            f.write(error)
                
