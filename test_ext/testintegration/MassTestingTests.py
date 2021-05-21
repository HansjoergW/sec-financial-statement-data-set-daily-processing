from _00_common.DebugUtils import DataAccessTool, TestSetCreatorTool
from _00_common.DBManagement import DBManager
from _02_xml.SecXmlPreParsing import SecPreXmlParser
from _02_xml.pre.SecPreXmlExtracting import SecPreXmlExtractor
from _02_xml.pre.SecPreXmlTransformation import SecPreXmlTransformer
from _02_xml.pre.SecPreXmlProcessing import SecPreXmlDataProcessor

from typing import List, Dict, Tuple
from multiprocessing import Pool
import logging
import pandas as pd


""" Idee::
hier irgendwie die einzelnen Tests als Klassen ablegen.
zB. prüfen ob Anzahl Reports identisch, Total und pro Typ -> das erste, was wir sicherstellen möchten.

Die einzelnen TestAspekte müssen separiert werden, sonst gibt es ein durcheinander

"""

default_workdir = "d:/secprocessing"
testsetcreator = TestSetCreatorTool(default_workdir)
dbmgr = DBManager(default_workdir)


# Tests
# 1. Adshs vergleichen
# 2. Anzahl Statements vergleichen
# 3. Statement typen vergleichen
# 4. Reihenfolge vergleichen (falls in der richtingen Reihenfolge geschrieben wurde)


if __name__ == '__main__':
    # test_preXmlParsing()
    pass