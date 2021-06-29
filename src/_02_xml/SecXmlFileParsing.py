# coordinates the parsing of donwloaded xml files and stores the data in a new folder
from _02_xml.parsing.SecXmlNumParsing import SecNumXmlParser
from _02_xml.parsing.SecXmlPreParsing import SecPreXmlParser
from _02_xml.parsing.SecXmlParsingBase import SecXmlParserBase
from _00_common.DBManagement import DBManager
from _00_common.SecFileUtils import read_content_from_zip, write_df_to_zip

import logging
import datetime
import os
import pandas as pd

from typing import List,Tuple,Callable
from multiprocessing import Pool


class SecXmlParser:

    def __init__(self, dbmanager: DBManager, data_dir: str = "./tmp/data/", use_process_date_in_path: bool = True):
        self.dbmanager = dbmanager
        self.processdate = datetime.date.today().isoformat()
        self.data_dir = data_dir

        if self.data_dir[-1] != '/':
            self.data_dir = data_dir + '/'

        if use_process_date_in_path:
            self.data_dir = self.data_dir + self.processdate + '/'

        if not os.path.isdir(self.data_dir):
            os.makedirs(self.data_dir)

        self.numparser = SecNumXmlParser()
        self.preparser = SecPreXmlParser()

    @staticmethod
    def _parse_file(data_tuple: Tuple[str]) -> (pd.DataFrame, str):
        accessionnr: str = data_tuple[0]
        xml_file: str = data_tuple[1]
        data_dir: str = data_tuple[2]
        parser: SecXmlParserBase = data_tuple[3]

        targetfilepath = data_dir + accessionnr + '_' + parser.get_type() + ".csv"

        xml_content = read_content_from_zip(xml_file)

        try:
            # todo: check if we should do something with the error_list
            df, error_list = parser.parse(accessionnr, xml_content)
            df = parser.clean_for_financial_statement_dataset(df, accessionnr)
            write_df_to_zip(df, targetfilepath)

            return (targetfilepath, accessionnr, 'parsed:'+ str(len(df)))
        except Exception as e:
            logging.exception("failed to parse data: " + xml_file, e)
            return (None, accessionnr, str(e))

    def _parse(self, parser: SecXmlParserBase, select_funct: Callable, update_funct: Callable):
        pool = Pool(8)

        missing: List[Tuple[str, str]] = select_funct()
        missing: List[Tuple[str, str, str, str]] = [(*entry, self.data_dir, parser) for entry in missing]
        logging.info("   missing entries " + str(len(missing)))

        for i in range(0, len(missing), 100):
            chunk = missing[i:i + 100]

            update_data: List[Tuple[str]] = pool.map(SecXmlParser._parse_file, chunk)
            update_data = [(entry[0], self.processdate, entry[2], entry[1]) for entry in update_data]

            update_funct(update_data)

            logging.info("   commited chunk: " + str(i))

        # todo failed berechnen oder aus update_data extrahieren

    def parseNumFiles(self):
        logging.info("parsing Num Files")
        self._parse(self.numparser, self.dbmanager.find_unparsed_numFiles, self.dbmanager.update_parsed_num_file)

    def parsePreFiles(self):
        logging.info("parsing Pre Files")
        self._parse(self.preparser, self.dbmanager.find_unparsed_preFiles, self.dbmanager.update_parsed_pre_file)