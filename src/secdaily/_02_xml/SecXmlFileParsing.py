# coordinates the parsing of downloaded xml files and stores the data in a new folder
import logging
import traceback
from typing import List, Protocol

from secdaily._00_common.ParallelExecution import ParallelExecutor
from secdaily._00_common.ProcessBase import ErrorEntry, ProcessBase
from secdaily._00_common.SecFileUtils import read_content_from_zip, write_df_to_zip
from secdaily._02_xml.db.XmlFileParsingDataAccess import (
    UnparsedFile,
    UpdateLabParsing,
    UpdateNumParsing,
    UpdatePreParsing,
)
from secdaily._02_xml.parsing.SecXmlLabParsing import SecLabXmlParser
from secdaily._02_xml.parsing.SecXmlNumParsing import SecNumXmlParser
from secdaily._02_xml.parsing.SecXmlPreParsing import SecPreXmlParser


class DataAccess(Protocol):

    def find_unparsed_numFiles(self) -> List[UnparsedFile]:
        """find report entries for which the xmlnumfiles have not been parsed"""
        return []

    def find_unparsed_preFiles(self) -> List[UnparsedFile]:
        """find report entries for which the xmlprefiles have not been parsed"""
        return []

    def find_unparsed_labFiles(self) -> List[UnparsedFile]:
        """find report entries for which the xmllabfiles have not been parsed"""
        return []

    def update_parsed_num_file(self, updatelist: List[UpdateNumParsing]):
        """update the report entry with the parsed result file"""

    def update_parsed_pre_file(self, updatelist: List[UpdatePreParsing]):
        """update the report entry with the parsed result file"""

    def update_parsed_lab_file(self, updatelist: List[UpdateLabParsing]):
        """update the report entry with the parsed result file"""


class SecXmlParser(ProcessBase):
    numparser = SecNumXmlParser()
    preparser = SecPreXmlParser()
    labparser = SecLabXmlParser()

    def __init__(self, dbmanager: DataAccess, data_dir: str = "./tmp/csv/"):
        super().__init__(data_dir=data_dir)

        self.dbmanager = dbmanager

    # --- Lab Parsing
    def _parse_lab_file(self, data: UnparsedFile) -> UpdateLabParsing:

        parser = SecXmlParser.labparser

        filename = data.accessionNumber + "_" + parser.get_type() + ".csv"
        filepath = self.data_path / data.get_qrtr_string() / data.get_filing_date() / filename

        xml_content = read_content_from_zip(data.file)

        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)

            df, error_list = parser.parse(data.accessionNumber, xml_content)
            self._log_error(data.accessionNumber, f"parse_{parser.get_type()}", error_list)
            write_df_to_zip(df, str(filepath))
            return UpdateLabParsing(
                accessionNumber=data.accessionNumber,
                csvLabFile=str(filepath),
                labParseDate=self.processdate,
                labParseState="parsed:" + str(len(df)),
            )

        except Exception as e: # pylint: disable=broad-except
            logging.exception("failed to parse data: %s / %s", data.file, e)
            self._log_error(
                adsh=data.accessionNumber,
                file_type=f"parse_failed_{parser.get_type()}",
                error_list=[ErrorEntry(adsh=data.accessionNumber, error_info=data.file, error=traceback.format_exc())],
            )
            return UpdateLabParsing(
                accessionNumber=data.accessionNumber,
                csvLabFile=None,
                labParseDate=self.processdate,
                labParseState=str(e),
            )

    def parseLabFiles(self):
        logging.info("parsing Lab Files")

        executor = ParallelExecutor[UnparsedFile, UpdateLabParsing, type(None)]()  # no limitation in speed

        executor.set_get_entries_function(self.dbmanager.find_unparsed_labFiles)
        executor.set_process_element_function(self._parse_lab_file)
        executor.set_post_process_chunk_function(self.dbmanager.update_parsed_lab_file)

        executor.execute()

    # --- Pre Parsing
    def _parse_pre_file(self, data: UnparsedFile) -> UpdatePreParsing:

        parser = SecXmlParser.preparser

        filename = data.accessionNumber + "_" + parser.get_type() + ".csv"
        filepath = self.data_path / data.get_qrtr_string() / data.get_filing_date() / filename

        xml_content = read_content_from_zip(data.file)

        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)

            df, error_list = parser.parse(data.accessionNumber, xml_content)
            self._log_error(data.accessionNumber, f"parse_{parser.get_type()}", error_list)
            write_df_to_zip(df, str(filepath))
            return UpdatePreParsing(
                accessionNumber=data.accessionNumber,
                csvPreFile=str(filepath),
                preParseDate=self.processdate,
                preParseState="parsed:" + str(len(df)),
            )

        except Exception as e: # pylint: disable=broad-except
            logging.exception("failed to parse data: %s / %s", data.file, e)
            self._log_error(
                adsh=data.accessionNumber,
                file_type=f"parse_failed_{parser.get_type()}",
                error_list=[ErrorEntry(adsh=data.accessionNumber, error_info=data.file, error=traceback.format_exc())],
            )
            return UpdatePreParsing(
                accessionNumber=data.accessionNumber,
                csvPreFile=None,
                preParseDate=self.processdate,
                preParseState=str(e),
            )

    def parsePreFiles(self):
        logging.info("parsing Pre Files")

        executor = ParallelExecutor[UnparsedFile, UpdatePreParsing, type(None)]()  # no limitation in speed

        executor.set_get_entries_function(self.dbmanager.find_unparsed_preFiles)
        executor.set_process_element_function(self._parse_pre_file)
        executor.set_post_process_chunk_function(self.dbmanager.update_parsed_pre_file)

        executor.execute()
        # todo failed berechnen oder aus update_data extrahieren

    # --- Num parsing
    def _parse_num_file(self, data: UnparsedFile) -> UpdateNumParsing:

        parser = SecXmlParser.numparser

        filename = data.accessionNumber + "_" + parser.get_type() + ".csv"
        filepath = self.data_path / data.get_qrtr_string() / data.get_filing_date() / filename

        xml_content = read_content_from_zip(data.file)

        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)

            df, error_list = parser.parse(data.accessionNumber, xml_content)
            self._log_error(data.accessionNumber, f"parse_{parser.get_type()}", error_list)

            # extract fiscal year end date
            # current fiscal year end appears in the form --MM-dd, so we remove the dashes
            df.loc[(df.tag == "CurrentFiscalYearEndDate"), "value"] = df[
                df.tag == "CurrentFiscalYearEndDate"
            ].value.str.replace("-", "")

            # check wether a currentfiscalyearenddate is present -> we return that as a separate information
            cfyed_df = df[(df.tag == "CurrentFiscalYearEndDate")]
            if len(cfyed_df) > 0:
                fiscalYearEnd = cfyed_df.value.iloc[0]
            else:
                fiscalYearEnd = None

            write_df_to_zip(df, str(filepath))
            return UpdateNumParsing(
                accessionNumber=data.accessionNumber,
                csvNumFile=str(filepath),
                numParseDate=self.processdate,
                numParseState="parsed:" + str(len(df)),
                fiscalYearEnd=fiscalYearEnd,
            )

        except Exception as e: # pylint: disable=broad-except
            logging.exception("failed to parse data: %s / %s", data.file, e)
            self._log_error(
                adsh=data.accessionNumber,
                file_type=f"parse_failed_{parser.get_type()}",
                error_list=[ErrorEntry(adsh=data.accessionNumber, error_info=data.file, error=traceback.format_exc())],
            )
            return UpdateNumParsing(
                accessionNumber=data.accessionNumber,
                csvNumFile=None,
                numParseDate=self.processdate,
                numParseState=str(e),
                fiscalYearEnd=None,
            )

    def parseNumFiles(self):
        logging.info("parsing Num Files")

        executor = ParallelExecutor[UnparsedFile, UpdateNumParsing, type(None)]()  # no limitation in speed

        executor.set_get_entries_function(self.dbmanager.find_unparsed_numFiles)
        executor.set_process_element_function(self._parse_num_file)
        executor.set_post_process_chunk_function(self.dbmanager.update_parsed_num_file)

        executor.execute()
        # todo failed berechnen oder aus update_data extrahieren
