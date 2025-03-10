from _00_common.DBManagement import DBManager
from _00_common.DebugUtils import DataAccessTool, TestSetCreatorTool
from _02_xml.parsing.SecXmlPreParsing import SecPreXmlParser
from _02_xml.parsing.SecXmlParsingBase import SecError
import pandas as pd
import os
from typing import Dict, List, Tuple
from multiprocessing import Pool

MASS_PRE_ZIP_TABLE = "mass_pre_zip_content"
MASS_PRE_XML_TABLE = "mass_pre_parse_xml_data"


def convert_to_mass_report_test_df(dbmgr: DBManager, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    pre_by_adsh_grouped = df.groupby(['adsh','report'])

    processing_df = dbmgr.read_all_processing()
    adsh_xmlPre_df = processing_df[['accessionNumber', 'xmlPreFile']]
    adsh_xmlPre_df.set_index('accessionNumber', inplace=True)

    adsh_xml_dict = adsh_xmlPre_df.to_dict('index')

    records: List[Dict[str,str]] = []
    missing_xml_files:List[str] = []
    for groupname, groupdf in pre_by_adsh_grouped:
        stmt = groupdf.stmt.tolist()[0]
        inpth = groupdf.inpth.tolist()[0]
        sorted_tags = groupdf[['tag','line']].sort_values(['line'])
        tags = sorted_tags.tag.tolist()
        adsh = groupname[0]
        report = groupname[1]

        try:
            # it could happen, that for some reason, the tagname is missing.
            tags = [str(tag) for tag in tags]
            taglist = ",".join(tags)

            # check
            if len(taglist.split(',')) != len(tags):
                raise Exception("tag contain ','!!")
            try:
                xmlFile = adsh_xml_dict[adsh]['xmlPreFile']
            except KeyError:
                missing_xml_files.append(adsh)
                xmlFile = None

            details = {}
            details['adsh'] = adsh
            details['report'] = report
            details['stmt'] = stmt
            details['length'] = len(tags)
            details['tagList'] = taglist
            details['xmlFile'] = xmlFile
            details['inpth'] = inpth

            records.append(details)
        except Exception as e:
            print(groupname, " - ", tags, " - ", str(e))

    return (pd.DataFrame.from_records(records), missing_xml_files)


class FillMassPreZipContent():
    """ prepares the most important information from pre.txt in the zip file in order for
        easier comparisson with the parsed content"""

    def __init__(self, dbmgr: DBManager, dataUtils: DataAccessTool, year: int, qrtr: int):
        self.dbmgr = dbmgr
        self.dataUtils = dataUtils
        self.zipfilePath = self.dataUtils._get_zipfilename(year,qrtr)
        self.zipfileName = os.path.basename(self.zipfilePath)

    def process(self):
        sub_df = self.dataUtils._read_file_from_zip(self.zipfilePath, 'sub.txt')
        sub_df = sub_df[sub_df.form.isin(['10-K', '10-Q'])]
        relevant_adsh = set(sub_df.adsh.tolist())

        pre_df = self.dataUtils._read_file_from_zip(self.zipfilePath, 'pre.txt')
        pre_df = pre_df[pre_df.adsh.isin(relevant_adsh)]

        print(pre_df.shape)

        pre_mass_df, missing_xml_files = convert_to_mass_report_test_df(self.dbmgr, pre_df)
        pre_mass_df['qrtrFile'] = self.zipfileName

        conn = self.dbmgr.get_connection()
        try:
            pre_mass_df.to_sql(MASS_PRE_ZIP_TABLE, conn, if_exists="append", chunksize=1000, index=False)
        finally:
            conn.close()

        print('mising xmlfiles: ', len(set(missing_xml_files)))


class ReadMassPreZipContent():
    """ reads the prezip content for a whole quarter back from db into a dataframe"""

    def __init__(self, dbmgr: DBManager, dataUtils: DataAccessTool, year: int, qrtr: int):
        self.dbmgr = dbmgr
        self.dataUtils = dataUtils
        self.zipfilePath = self.dataUtils._get_zipfilename(year,qrtr)
        self.zipfileName = os.path.basename(self.zipfilePath)

    def readContent(self, adshs: List[str] = None) -> pd.DataFrame:
        conn = self.dbmgr.get_connection()
        try:
            sql = '''SELECT * FROM {} WHERE qrtrFile='{}'  '''.format(MASS_PRE_ZIP_TABLE, self.zipfileName)
            df = pd.read_sql_query(sql, conn)
            if adshs is not None:
                df = df[df.adsh.isin(adshs)].copy()
            return df
        finally:
            conn.close()


class FillMassParseContent():

    def __init__(self, dbmgr: DBManager, testsetcreator: TestSetCreatorTool, year: int, months: List[int]):
        self.dbmgr = dbmgr
        self.testsetcreator = testsetcreator
        self.year = year
        self.months: List[int] = months

    @staticmethod
    def prepare_func(data: Tuple[str, str]) -> Tuple[pd.DataFrame, List[SecError]]:
        pre_xml_parser = SecPreXmlParser()

        adsh = data[0]
        pre_xml_file = data[1]
        try:
            with open(pre_xml_file, "r", encoding="utf-8") as f:
                content: str = f.read()
                df: pd.DataFrame
                errors: List[SecError]
                df, errors  = pre_xml_parser.parse(adsh, content)
                df = pre_xml_parser.clean_for_financial_statement_dataset(df, adsh)

                return (df, errors)
        except Exception as e:
            return (None, [SecError(adsh, pre_xml_file, str(e))])

    def process(self):
        # complete run needs about 4 minutes (first time to load data in disk-cache, afterwards about 100secs)
        # executes the complete parsing on all of the available reports from the
        # provided year and months
        adshs: List[str] = self.testsetcreator.get_testset_by_year_and_months(self.year, self.months)
        xml_files_info: List[Tuple[str, str, str]] = self.dbmgr.get_xml_files_info_from_sec_processing_by_adshs(adshs)
        pre_xml_files_info: List[Tuple[str, str]] = [(x[0], x[2]) for x in xml_files_info] # adsh and preXmlFile

        pool = Pool(8)

        all_failed: List[SecError] = []
        all_dfs: List[pd.DataFrame] = []

        print("adsh to test: ", len(adshs))
        for i in range(0, len(pre_xml_files_info), 500):
            chunk = pre_xml_files_info[i:i + 500]

            result: List[pd.DataFrame, List[SecError]] = pool.map(FillMassParseContent.prepare_func, chunk)

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

        xml_mass_df, missing_xml_files = convert_to_mass_report_test_df(self.dbmgr, all_df)

        conn = self.dbmgr.get_connection()
        try:
            xml_mass_df.to_sql(MASS_PRE_XML_TABLE, conn, if_exists="append", chunksize=1000, index=False)
        finally:
            conn.close()

        print('mising xmlfiles: ', len(set(missing_xml_files)))


class ReadMassPreXmlContent():
    """ reads the prezip content for a whole quarter back from db into a dataframe"""

    def __init__(self, dbmgr: DBManager):
        self.dbmgr = dbmgr

    def readContent(self, adshs: List[str] = None) -> pd.DataFrame:
        conn = self.dbmgr.get_connection()
        try:
            sql = '''SELECT * FROM {} '''.format(MASS_PRE_XML_TABLE)
            df = pd.read_sql_query(sql, conn)
            if adshs is not None:
                df = df[df.adsh.isin(adshs)].copy()
            return df
        finally:
            conn.close()


def fill_mass_pre_zip(dbmgr: DBManager, dataUtils: DataAccessTool, year: int, qrtr: int):
    content_filler = FillMassPreZipContent(dbmgr, dataUtils, year, qrtr)
    content_filler.process()


def read_mass_pre_zip_content(dbmgr: DBManager, dataUtils: DataAccessTool, year:int, qrtr: int, adshs: List[str] = None) -> pd.DataFrame :
    reader = ReadMassPreZipContent(dbmgr, dataUtils, year, qrtr)
    return reader.readContent(adshs)


def fill_mass_pre_xml(dbmgr: DBManager, testsetcreator: TestSetCreatorTool, year: int, months: List[int]):
    content_filler = FillMassParseContent(dbmgr, testsetcreator, year, months)
    content_filler.process()


def read_mass_pre_xml_content(dbmgr: DBManager, adshs: List[str] = None) -> pd.DataFrame :
    reader = ReadMassPreXmlContent(dbmgr)
    return reader.readContent(adshs)


if __name__ == '__main__':
    workdir = "d:/secprocessing/"
    dbmgr = DBManager(workdir)
    dataUtils = DataAccessTool(workdir)
    testCreatorTool = TestSetCreatorTool(workdir)

    #fill_mass_pre_zip(dbmgr, dataUtils, 2021, 1)
    #df = read_mass_pre_zip_content(dbmgr, dataUtils, 2021, 1)
    #print(df.shape)
    print('start xml')
    fill_mass_pre_xml(dbmgr, testCreatorTool, 2021, [1,2,3])

