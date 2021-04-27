# coordinates the parsing of donwloaded xml files and stores the data in a new folder
from _02_xml.SecXmlNumParsing import SecNumXmlParser
from _02_xml.SecXmlPreParsing import SecPreXmlParser
from _00_common.DBManagement import DBManager

import logging
import datetime
import os

from typing import List,Tuple,Callable
from time import time, sleep
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

