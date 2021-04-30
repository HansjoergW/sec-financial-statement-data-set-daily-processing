# coordinates the parsing of donwloaded xml files and stores the data in a new folder
from _02_xml.SecXmlNumParsing import SecNumXmlParser
from _02_xml.SecXmlPreParsing import SecPreXmlParser
from _02_xml.SecXmlParsingBase import SecXmlParserBase
from _00_common.DBManagement import DBManager

import logging
import datetime
import os
import pandas as pd

from typing import List,Tuple,Callable
from multiprocessing import Pool


class SecXmlParser:

    def __init__(self, dbmanager: DBManager, data_dir: str = "./tmp/data/"):
        self.dbmanager = dbmanager
        self.processdate = datetime.date.today().isoformat()

        if data_dir[-1] != '/':
            data_dir = data_dir + '/'

        self.data_dir = data_dir + self.processdate + '/'

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

        # filename = xml_file.rsplit('/', 1)[-1]
        # filename = filename.rsplit('.', 1)[0] + ".csv" # remove xml at end and add csv instead
        targetfilepath = data_dir + accessionnr + '_' + parser.get_type() + ".csv"

        with open(xml_file, "r", encoding="utf-8") as f:
            xml_content = f.read()

            try:
                df = parser.parse(xml_content)
                df = parser.clean_for_financial_statement_dataset(df, accessionnr)
                df.to_csv(targetfilepath, header=True, sep="\t")

                return (targetfilepath, accessionnr)
            except Exception as e:
                logging.exception("failed to parse data: " + xml_file, e)
                return (None, accessionnr)

    def _parse(self, parser: SecXmlParserBase, select_funct: Callable, update_funct: Callable):
        pool = Pool(8)

        missing:List[Tuple[str]] = select_funct()
        missing = [(*entry, self.data_dir, parser) for entry in missing]

        for i in range(0, len(missing), 100):
            chunk = missing[i:i + 100]

            update_data: List[Tuple[str]] = pool.map(SecXmlParser._parse_file, chunk)

            #todo update logic
            # add additional infos, ignore None values in update_data
            #update_funct(update_data)

            logging.info("   commited chunk: " + str(i))

        # todo failed berechnen oder aus update_data extrahieren


    def parseNumFiles(self):
        logging.info("processing Num Files")
        self._parse(self.numparser, self.dbmanager.find_unparsed_numFiles, self.dbmanager.update_parsed_num_file)

    def parsePreFiles(self):
        logging.info("processing Pre Files")
        self._parse(self.preparser, self.dbmanager.find_unparsed_preFiles, self.dbmanager.update_parsed_pre_file)