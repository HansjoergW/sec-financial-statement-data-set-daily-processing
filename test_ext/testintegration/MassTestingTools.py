from _00_common.DBManagement import DBManager
from _00_common.DebugUtils import DataAccessTool
import pandas as pd
import os
from typing import Dict, List

MASS_PRE_ZIP_TABLE = "mass_pre_zip_content"

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

        pre_by_adsh_grouped = pre_df.groupby(['adsh','report'])

        processing_df = self.dbmgr.read_all_processing()
        adsh_xmlPre_df = processing_df[['accessionNumber', 'xmlPreFile']]
        adsh_xmlPre_df.set_index('accessionNumber', inplace=True)

        adsh_xml_dict = adsh_xmlPre_df.to_dict('index')

        records: List[Dict[str,str]] = []
        missing_xml_files:List[str] = []
        for groupname, groupdf in pre_by_adsh_grouped:
            stmt = groupdf.stmt.tolist()[0]
            tags = groupdf.tag.tolist()
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
                details['qrtrFile'] = self.zipfileName

                records.append(details)
            except Exception as e:
                print(groupname, " - ", tags, " - ", str(e))

        pre_mass_df = pd.DataFrame.from_records(records)

        conn = self.dbmgr.get_connection()
        try:
            pre_mass_df.to_sql(MASS_PRE_ZIP_TABLE, conn, if_exists="append", chunksize=1000, index=False)
        finally:
            conn.close()

        print('mising xmlfiles: ', len(set(missing_xml_files)))


class ReadMassPreZipContent():

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


def fill_mass_pre_zip(dbmgr: DBManager, dataUtils: DataAccessTool, year: int, qrtr: int):
    content_filler = FillMassPreZipContent(dbmgr, dataUtils, year, qrtr)
    content_filler.process()


def read_mass_pre_zip_content(dbmgr: DBManager, dataUtils: DataAccessTool, year:int, qrtr: int) -> pd.DataFrame :
    reader = ReadMassPreZipContent(dbmgr, dataUtils, 2021, 1)
    return reader.readContent()


if __name__ == '__main__':
    workdir = "d:/secprocessing/"
    dbmgr = DBManager(workdir)
    dataUtils = DataAccessTool(workdir)

    #fill_mass_pre_zip(dbmgr, dataUtils, 2021, 1)
    df = read_mass_pre_zip_content(dbmgr, dataUtils, 2021, 1)
    print(df.shape)


