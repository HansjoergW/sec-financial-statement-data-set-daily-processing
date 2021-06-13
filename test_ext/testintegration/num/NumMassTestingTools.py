from _00_common.DBManagement import DBManager
from _00_common.DebugUtils import DataAccessTool, TestSetCreatorTool
from _02_xml.SecXmlNumParsing import SecNumXmlParser
from _02_xml.SecXmlParsingBase import SecError
import pandas as pd
import os
from typing import Dict, List, Tuple
from multiprocessing import Pool

ALL_PARSED_NUM_CONTENT_FILE = "d:/secprocessing/tmp/all_num.csv"

class CreateAllNumParseContent():

    def __init__(self, dbmgr: DBManager, testsetcreator: TestSetCreatorTool, year: int, months: List[int]):
        self.dbmgr = dbmgr
        self.testsetcreator = testsetcreator
        self.year = year
        self.months: List[int] = months

    @staticmethod
    def prepare_func(data: Tuple[str, str]) -> Tuple[pd.DataFrame, List[SecError]]:
        pre_num_parser = SecNumXmlParser()

        adsh = data[0]
        num_xml_file = data[1]
        try:
            with open(num_xml_file, "r", encoding="utf-8") as f:
                content: str = f.read()
                df: pd.DataFrame
                errors: List[SecError]
                df, errors  = pre_num_parser.parse(adsh, content)
                df = pre_num_parser.clean_for_financial_statement_dataset(df, adsh)

                return (df, errors)
        except Exception as e:
            return (None, [SecError(adsh, num_xml_file, str(e))])

    def process(self):
        # complete run needs about 4 minutes (first time to load data in disk-cache, afterwards about 100secs)
        # executes the complete parsing on all of the available reports from the
        # provided year and months
        adshs: List[str] = self.testsetcreator.get_testset_by_year_and_months(self.year, self.months)
        xml_files_info: List[Tuple[str, str, str]] = self.dbmgr.get_xml_files_info_from_sec_processing_by_adshs(adshs)
        num_xml_files_info: List[Tuple[str, str]] = [(x[0], x[1]) for x in xml_files_info] # adsh and preXmlFile

        pool = Pool(8)

        all_failed: List[SecError] = []
        all_dfs: List[pd.DataFrame] = []

        print("adsh to test: ", len(adshs))
        for i in range(0, len(num_xml_files_info), 500):
            chunk = num_xml_files_info[i:i + 500]

            result: List[pd.DataFrame, List[SecError]] = pool.map(CreateAllNumParseContent.prepare_func, chunk)

            print(".", end="")
            for entry in result:
                all_failed.extend(entry[1])
                all_dfs.append(entry[0])

        all_failed = [x for x in all_failed if x is not None]
        # Attention: prints the failed for all entries, not only primary financial statement canditates
        for failed in all_failed:
            failed.printentry()

        all_df = pd.concat(all_dfs)
        all_df.reset_index(inplace=True)

        all_df.to_csv(ALL_PARSED_NUM_CONTENT_FILE, index=False, header=True, sep="\t")
        print("entries: ", len(all_df))


class ReadCreatedNumXmlContent():
    """ reads the prezip content for a whole quarter back from db into a dataframe"""

    def __init__(self):
        pass

    def readContent(self, adshs: List[str] = None) -> pd.DataFrame:
        df = pd.read_csv(ALL_PARSED_NUM_CONTENT_FILE, header=0, sep="\t")
        if adshs is not None:
            df = df[df.adsh.isin(adshs)].copy()
        return df


class ReadNumZipContent():

    def __init__(self, dataUtils: DataAccessTool, year: int, qrtr: int):
        self.dataUtils = dataUtils
        self.zipfilePath = self.dataUtils._get_zipfilename(year,qrtr)
        self.zipfileName = os.path.basename(self.zipfilePath)

    def readContent(self, adshs: List[str] = None) ->pd.DataFrame:
        sub_df = self.dataUtils._read_file_from_zip(self.zipfilePath, 'sub.txt')
        sub_df = sub_df[sub_df.form.isin(['10-K', '10-Q'])]
        relevant_adsh = set(sub_df.adsh.tolist())

        pre_df = self.dataUtils._read_file_from_zip(self.zipfilePath, 'num.txt')
        pre_df = pre_df[pre_df.adsh.isin(relevant_adsh)]

        return pre_df


def create_all_num_xml(dbmgr: DBManager, testsetcreator: TestSetCreatorTool, year: int, months: List[int]):
    content_filler = CreateAllNumParseContent(dbmgr, testsetcreator, year, months)
    content_filler.process()


def read_mass_num_zip_content(dataUtils: DataAccessTool, year: int, qrtr: int, adshs: List[str] = None) -> pd.DataFrame:
    reader = ReadNumZipContent(dataUtils, year, qrtr)
    return reader.readContent(adshs)


def read_mass_num_xml_content(adshs: List[str] = None) -> pd.DataFrame :
    reader = ReadCreatedNumXmlContent()
    return reader.readContent(adshs)


if __name__ == '__main__':
    workdir = "d:/secprocessing/"
    dbmgr = DBManager(workdir)
    dataUtils = DataAccessTool(workdir)
    testCreatorTool = TestSetCreatorTool(workdir)

    #fill_mass_pre_zip(dbmgr, dataUtils, 2021, 1)
    #df = read_mass_pre_zip_content(dbmgr, dataUtils, 2021, 1)
    #print(df.shape)
    create_all_num_xml(dbmgr, testCreatorTool, 2021, [1,2,3])
    # df = read_mass_num_xml_content()
    # print(df.shape)