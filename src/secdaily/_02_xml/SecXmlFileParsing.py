# coordinates the parsing of downloaded xml files and stores the data in a new folder
import datetime
import logging
import os
from typing import Protocol, List, Tuple

from secdaily._02_xml.db.XmlFileParsingDataAccess import UpdateNumParsing, UnparsedFile, UpdatePreParsing, UpdateLabParsing
from secdaily._00_common.ParallelExecution import ParallelExecutor
from secdaily._00_common.SecFileUtils import read_content_from_zip, write_df_to_zip
from secdaily._02_xml.parsing.SecXmlNumParsing import SecNumXmlParser
from secdaily._02_xml.parsing.SecXmlParsingBase import SecError
from secdaily._02_xml.parsing.SecXmlPreParsing import SecPreXmlParser
from secdaily._02_xml.parsing.SecXmlLabParsing import SecLabXmlParser

class DataAccess(Protocol):

    def find_unparsed_numFiles(self) -> List[UnparsedFile]:
        """ find report entries for which the xmlnumfiles have not been parsed """
        return []

    def find_unparsed_preFiles(self) -> List[UnparsedFile]:
        """ find report entries for which the xmlprefiles have not been parsed """
        return []

    def find_unparsed_labFiles(self) -> List[UnparsedFile]:
        """ find report entries for which the xmllabfiles have not been parsed """
        return []

    def update_parsed_num_file(self, updatelist: List[UpdateNumParsing]):
        """ update the report entry with the parsed result file """

    def update_parsed_pre_file(self, updatelist: List[UpdatePreParsing]):
        """ update the report entry with the parsed result file """

    def update_parsed_lab_file(self, updatelist: List[UpdateLabParsing]):
        """ update the report entry with the parsed result file """


class SecXmlParser:
    numparser = SecNumXmlParser()
    preparser = SecPreXmlParser()
    labparser = SecLabXmlParser()

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
    

    def _log_parse_errors(self, adsh: str, type: str, error_list: List[SecError]):
        if len(error_list) > 0:
            error_file_name = self.error_log_dir + "parse_" + type + "_" + adsh + ".txt"
            with open(error_file_name, "w", encoding="utf-8") as f:
                for error in error_list:
                    f.write(error.report_role + " - " + error.error + "\n")


    # --- Lab Parsing
    def _parse_lab_file(self, data: UnparsedFile) -> UpdateLabParsing:

        parser = SecXmlParser.labparser

        targetfilepath = self.data_dir + data.accessionNumber + '_' + parser.get_type() + ".csv"

        xml_content = read_content_from_zip(data.file)

        try:
            df, error_list = parser.parse(data.accessionNumber, xml_content)
            self._log_parse_errors(data.accessionNumber, parser.get_type(), error_list)
            write_df_to_zip(df, targetfilepath)
            return UpdateLabParsing(
                accessionNumber=data.accessionNumber,
                csvLabFile=targetfilepath,
                labParseDate=self.processdate,
                labParseState='parsed:' + str(len(df))
            )

        except Exception as e:
            logging.exception("failed to parse data: " + data.file, e)
            return UpdateLabParsing(
                accessionNumber=data.accessionNumber,
                csvLabFile=None,
                labParseDate=self.processdate,
                labParseState=str(e))
    
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

        targetfilepath = self.data_dir + data.accessionNumber + '_' + parser.get_type() + ".csv"

        xml_content = read_content_from_zip(data.file)

        try:
            # todo: check if we should do something with the error_list
            df, error_list = parser.parse(data.accessionNumber, xml_content)
            self._log_parse_errors(data.accessionNumber, parser.get_type(), error_list)
            write_df_to_zip(df, targetfilepath)
            return UpdatePreParsing(
                accessionNumber=data.accessionNumber,
                csvPreFile=targetfilepath,
                preParseDate=self.processdate,
                preParseState='parsed:' + str(len(df))
            )

        except Exception as e:
            logging.exception("failed to parse data: " + data.file, e)
            return UpdatePreParsing(
                accessionNumber=data.accessionNumber,
                csvPreFile=None,
                preParseDate=self.processdate,
                preParseState=str(e))

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

        targetfilepath = self.data_dir + data.accessionNumber + '_' + parser.get_type() + ".csv"

        xml_content = read_content_from_zip(data.file)

        try:
            df, error_list = parser.parse(data.accessionNumber, xml_content)
            self._log_parse_errors(data.accessionNumber, parser.get_type(), error_list)

            # extract fiscal year end date
            # current fiscal year end appears in the form --MM-dd, so we remove the dashes
            df.loc[(df.tag == 'CurrentFiscalYearEndDate'), 'value'] = df[df.tag == 'CurrentFiscalYearEndDate'].value.str.replace('-','')

            # check wether a currentfiscalyearenddate is present -> we return that as a separate information
            cfyed_df = df[(df.tag == 'CurrentFiscalYearEndDate')]
            if len(cfyed_df) > 0:
                fiscalYearEnd = cfyed_df.value.iloc[0]
            else:
                fiscalYearEnd = None            

            write_df_to_zip(df, targetfilepath)
            return UpdateNumParsing(accessionNumber=data.accessionNumber,
                                    csvNumFile=targetfilepath,
                                    numParseDate=self.processdate,
                                    numParseState='parsed:' + str(len(df)),
                                    fiscalYearEnd=fiscalYearEnd)

        except Exception as e:
            logging.exception("failed to parse data: " + data.file, e)
            return UpdateNumParsing(accessionNumber=data.accessionNumber,
                                    csvNumFile=None,
                                    numParseDate=self.processdate,
                                    numParseState=str(e),
                                    fiscalYearEnd=None)

    def parseNumFiles(self):
        logging.info("parsing Num Files")

        executor = ParallelExecutor[UnparsedFile, UpdateNumParsing, type(None)]()  # no limitation in speed

        executor.set_get_entries_function(self.dbmanager.find_unparsed_numFiles)
        executor.set_process_element_function(self._parse_num_file)
        executor.set_post_process_chunk_function(self.dbmanager.update_parsed_num_file)

        executor.execute()
        # todo failed berechnen oder aus update_data extrahieren
