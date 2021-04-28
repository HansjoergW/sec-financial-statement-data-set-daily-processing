# coordinates the parsing of donwloaded xml files and stores the data in a new folder
from _02_xml.SecXmlNumParsing import SecNumXmlParser
from _02_xml.SecXmlPreParsing import SecPreXmlParser
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

        # todo: superklasse für Paser -> mit parse und clean_for_pure Methoden
        # problem: pre parse hat andere p arameter -> flag für html oder xml ->
        # war im 2020 Q4 aber immer nur H -> evtl. auf neutralen Wert setzen und beim Vergleichen ignorieren
        self.numparser = SecNumXmlParser()
        self.preparser = SecPreXmlParser()


    @staticmethod
    def _parse_file(data_tuple: Tuple[str]) -> (pd.DataFrame, str):
        accessionnr: str = data_tuple[0]
        xml_file: str = data_tuple[1]
        data_dir: str = data_tuple[2]
        parser = data_tuple[3]

        filename = xml_file.rsplit('/', 1)[-1]
        filename = filename.rsplit('.', 1)[-1] + "csv" # remove xml at end and add csv instead
        targetfilepath = data_dir + filename

        with open(xml_file, "r", encoding="utf-8") as f:
            xml_content = f.read()
            try:
                parser.parse(xml_content)
                return (filepath, accessionnr)
            except:
                logging.warning("failed to download from: " + xml_file)
                return (None, accessionnr)


    def _parse(self, parser, select_funct: Callable, update_funct: Callable):
        pool = Pool(8)

        missing:List[Tuple[str]] = select_funct()
        missing = [(*entry, self.data_dir, parser) for entry in missing]

        for i in range(0, len(missing), 100):
            chunk = missing[i:i + 100]

            update_data: List[Tuple[str]] = pool.map(SecXmlFileProcessor._download_file_throttle, chunk)
            update_funct(update_data)

            logging.info("   commited chunk: " + str(i))

        # todo failed berechnen oder aus update_data extrahieren


    def parseNumFiles(self):
        logging.info("processing Num Files")
        self._parse(self.numparser, self.dbmanager.find_unparsed_numFiles, self.dbmanager.update_parsed_num_file)

    def parsePreFiles(self):
        logging.info("processing Pre Files")
        self._parse(self.preparser, self.dbmanager.find_unparsed_preFiles, self.dbmanager.update_parsed_pre_file)