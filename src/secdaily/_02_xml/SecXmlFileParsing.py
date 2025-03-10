# coordinates the parsing of downloaded xml files and stores the data in a new folder
import datetime
import logging
import os
from typing import Protocol, List, Tuple

from secdaily._02_xml.db.XmlFileParsingDataAccess import UpdateNumParsing, UnparsedFile, UpdatePreParsing
from secdaily._00_common.ParallelExecution import ParallelExecutor
from secdaily._00_common.SecFileUtils import read_content_from_zip, write_df_to_zip
from secdaily._02_xml.parsing.SecXmlNumParsing import SecNumXmlParser
from secdaily._02_xml.parsing.SecXmlPreParsing import SecPreXmlParser


class DataAccess(Protocol):

    def find_unparsed_numFiles(self) -> List[UnparsedFile]:
        """ find report entries for which the xmlnumfiles have not been parsed """

    def find_unparsed_preFiles(self) -> List[UnparsedFile]:
        """ find report entries for which the xmlprefiles have not been parsed """

    def update_parsed_num_file(self, updatelist: List[UpdateNumParsing]):
        """ update the report entry with the parsed result file """

    def update_parsed_pre_file(self, updatelist: List[UpdatePreParsing]):
        """ update the report entry with the parsed result file """


class SecXmlParser:
    numparser = SecNumXmlParser()
    preparser = SecPreXmlParser()

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

    # --- Pre Parsing
    def _parse_pre_file(self, data: UnparsedFile) -> UpdatePreParsing:

        parser = SecXmlParser.preparser

        targetfilepath = self.data_dir + data.accessionNumber + '_' + parser.get_type() + ".csv"

        xml_content = read_content_from_zip(data.file)

        try:
            # todo: check if we should do something with the error_list
            df, error_list = parser.parse(data.accessionNumber, xml_content)
            df = parser.clean_for_financial_statement_dataset(df, data.accessionNumber)
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
            df, fye = parser.clean_for_financial_statement_dataset(df, data.accessionNumber)

            write_df_to_zip(df, targetfilepath)
            return UpdateNumParsing(accessionNumber=data.accessionNumber,
                                    csvNumFile=targetfilepath,
                                    numParseDate=self.processdate,
                                    numParseState='parsed:' + str(len(df)),
                                    fiscalYearEnd=fye)

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
