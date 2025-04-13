import logging
import traceback
from typing import List, Protocol

from secdaily._00_common.BaseDefinitions import DTYPES_LAB, DTYPES_NUM, DTYPES_PRE
from secdaily._00_common.ParallelExecution import ParallelExecutor
from secdaily._00_common.ProcessBase import ErrorEntry, ProcessBase
from secdaily._00_common.SecFileUtils import read_df_from_zip, write_df_to_zip
from secdaily._03_secstyle.db.SecStyleFormatterDataAccess import UnformattedReport, UpdateStyleFormatting
from secdaily._03_secstyle.formatting.SECPreNumFormatting import SECPreNumFormatter


class DataAccess(Protocol):
    def find_unformatted_reports(self) -> List[UnformattedReport]:
        """find report entries which have not been formatted"""
        return []

    def update_formatted_reports(self, update_list: List[UpdateStyleFormatting]):
        """update the report entry with the formatted result file"""


class SECStyleFormatter(ProcessBase):

    prenumformatter = SECPreNumFormatter()

    def __init__(self, dbmanager: DataAccess, data_dir: str = "./tmp/secstyle/"):
        super().__init__(data_dir=data_dir)

        self.dbmanager = dbmanager

    def _format_report(self, data: UnformattedReport) -> UpdateStyleFormatting:
        # todo: we should provide the dtype here, to make sure we read the data in the correct format

        adsh = data.accessionNumber

        try:
            num_df = read_df_from_zip(data.numFile, dtype=DTYPES_NUM)
            pre_df = read_df_from_zip(data.preFile, dtype=DTYPES_PRE)
            lab_df = read_df_from_zip(data.labFile, dtype=DTYPES_LAB)

            filename_pre = adsh + "_pre.csv"
            filename_num = adsh + "_num.csv"

            filepath_pre = self.data_path / data.get_qrtr_string() / data.get_filing_date() / filename_pre
            filepath_num = self.data_path / data.get_qrtr_string() / data.get_filing_date() / filename_num

            filepath_pre.parent.mkdir(parents=True, exist_ok=True)

            pre_df, num_df, error_list = self.prenumformatter.format(
                adsh=adsh, pre_df=pre_df, num_df=num_df, lab_df=lab_df
            )

            self._log_error(data.accessionNumber, "format_prenum", error_list)

            write_df_to_zip(pre_df, str(filepath_pre))
            write_df_to_zip(num_df, str(filepath_num))
            return UpdateStyleFormatting(
                accessionNumber=data.accessionNumber,
                numFormattedFile=str(filepath_pre),
                preFormattedFile=str(filepath_num),
                formatDate=self.processdate,
                formatState="formatted",
            )

        except Exception as e:  # pylint: disable=broad-except
            logging.exception("failed to parse data for adsh: %s / %s", adsh, e)
            self._log_error(
                adsh=data.accessionNumber,
                file_type="parse_failed_format_prenum",
                error_list=[
                    ErrorEntry(
                        adsh=data.accessionNumber,
                        error_info=f"{data.preFile} / {data.numFile} / {data.labFile}",
                        error=traceback.format_exc(),
                    )
                ],
            )
            return UpdateStyleFormatting(
                accessionNumber=data.accessionNumber,
                numFormattedFile=None,
                preFormattedFile=None,
                formatDate=self.processdate,
                formatState=str(e),
            )

    def process(self):
        logging.info("SEC style formatting")

        executor = ParallelExecutor[UnformattedReport, UpdateStyleFormatting, type(None)]()  # no limitation in speed

        executor.set_get_entries_function(self.dbmanager.find_unformatted_reports)
        executor.set_process_element_function(self._format_report)
        executor.set_post_process_chunk_function(self.dbmanager.update_formatted_reports)

        executor.execute()
