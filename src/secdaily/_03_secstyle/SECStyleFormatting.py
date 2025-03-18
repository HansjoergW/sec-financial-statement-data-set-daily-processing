import datetime
import logging
import os
from typing import List, Optional, Protocol, Tuple
import numpy as np
import pandas as pd

from secdaily._00_common.ParallelExecution import ParallelExecutor
from secdaily._00_common.SecFileUtils import read_df_from_zip, write_df_to_zip
from secdaily._03_secstyle.db.SecStyleFormatterDataAccess import UnformattedReport, UpdateStyleFormatting
from secdaily._03_secstyle.formatting.SECPreNumFormatting import SECPreNumFormatter


class DataAccess(Protocol):
    def find_unformatted_reports(self) -> List[UnformattedReport]:
        """ find report entries which have not been formatted """
        return []

    def update_formatted_reports(self, update_list: List[UpdateStyleFormatting]):
        """ update the report entry with the formatted result file """


class SECStyleFormatter:

    prenumformatter = SECPreNumFormatter()

    def __init__(self, dbmanager: DataAccess, data_dir: str = "./tmp/data/", use_process_date_in_path: bool = True):  
        self.dbmanager = dbmanager
        self.processdate = datetime.date.today().isoformat()
        self.data_dir = data_dir

        if self.data_dir[-1] != '/':
            self.data_dir = data_dir + '/'

        if use_process_date_in_path:
            self.data_dir = self.data_dir + self.processdate + '/'

        if not os.path.isdir(self.data_dir):
            os.makedirs(self.data_dir)

        self.error_log_dir = self.data_dir + "error/"
        if not os.path.isdir(self.error_log_dir):
            os.makedirs(self.error_log_dir)



    def _format_report(self, data: UnformattedReport) -> UpdateStyleFormatting:
        
        num_df = read_df_from_zip(data.numFile)
        pre_df = read_df_from_zip(data.preFile)
        lab_df = read_df_from_zip(data.labFile)
        
        adsh = data.accessionNumber

        targetfilepath_pre = self.data_dir + adsh + '_pre.csv'
        targetfilepath_num = self.data_dir + adsh + '_num.csv'

        try:
            pre_df, num_df = self.prenumformatter.format(adsh=adsh, pre_df=pre_df, num_df=num_df, lab_df=lab_df)

            self._log_parse_errors(data.accessionNumber, parser.get_type(), error_list)
            write_df_to_zip(pre_df, targetfilepath_pre)
            write_df_to_zip(num_df, targetfilepath_num)
            return UpdateStyleFormatting(
                accessionNumber=data.accessionNumber,
                numFormattedFile=targetfilepath_pre,
                preFormattedFile=targetfilepath_num,
                formatDate=self.processdate,
                formatState='formatted')

        except Exception as e:
            logging.exception("failed to parse data for adsh: " + adsh, e)
            return UpdateStyleFormatting(
                accessionNumber=data.accessionNumber,
                numFormattedFile=None,
                preFormattedFile=None,
                formatDate=self.processdate,
                formatState=str(e))

    def process(self):
        logging.info("SEC style formatting")

        executor = ParallelExecutor[UnformattedReport, UpdateStyleFormatting, type(None)]()  # no limitation in speed

        executor.set_get_entries_function(self.dbmanager.find_unformatted_reports)
        executor.set_process_element_function(self._format_report)
        executor.set_post_process_chunk_function(self.dbmanager.update_formatted_reports)

        executor.execute()
