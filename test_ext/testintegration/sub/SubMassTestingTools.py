from _00_common.DBManagement import DBManager
from _00_common.DebugUtils import DataAccessTool, TestSetCreatorTool

from typing import List
import os
import pandas as pd
import glob


class ReadSubZipContent:
    """ prepares the most important information from pre.txt in the zip file in order for
        easier comparisson with the parsed content"""

    def __init__(self, dbmgr: DBManager, dataUtils: DataAccessTool, year: int, qrtr: int):
        self.dbmgr = dbmgr
        self.dataUtils = dataUtils
        self.zipfilePath = self.dataUtils._get_zipfilename(year,qrtr)
        self.zipfileName = os.path.basename(self.zipfilePath)

    def read_df(self, adshs: List[str] = None) -> pd.DataFrame:
        sub_df = self.dataUtils._read_file_from_zip(self.zipfilePath, 'sub.txt')
        sub_df = sub_df[sub_df.form.isin(['10-K', '10-Q'])]

        if adshs is not None:
            sub_df = sub_df[sub_df.adsh.isin(adshs)]

        return sub_df


class ReadSubXmlContent:

    def __init__(self, dbmgr: DBManager, testsetCreator: TestSetCreatorTool, year: int, qrtr: int):
        self.dbmgr = dbmgr
        self.testsetCreator = testsetCreator
        self.year = year
        self.qrtr = qrtr

    def read_df(self, adshs: List[str] = None) -> pd.DataFrame:
        daily_qrtr_path = self.testsetCreator.tool.dailyzipdir + str(self.year) + "q" + str(self.qrtr)

        daily_zips: List[str] = glob.glob("{0}/*.zip".format(daily_qrtr_path))

        df_list = []
        for daily_zip in daily_zips:
            sub_df = self.testsetCreator.tool._read_file_from_zip(daily_zip, "sub.txt")
            df_list.append(sub_df)

        return pd.concat(df_list)


def read_sub_zip_content(dbmgr: DBManager, dataUtils: DataAccessTool, year: int, qtr: int, adshs: List[str] = None) -> pd.DataFrame:
    reader = ReadSubZipContent(dbmgr, dataUtils, year, qtr)
    return reader.read_df(adshs)


def read_sub_xml_content(dbmgr: DBManager,testsetCreator: TestSetCreatorTool, year: int, qrtr:int, adshs: List[str] = None) -> pd.DataFrame:
    reader = ReadSubXmlContent(dbmgr, testsetCreator, year, qrtr)
    return reader.read_df(adshs)



