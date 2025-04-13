import zipfile
from typing import List, Optional, Tuple

import pandas as pd

from secdaily._00_common.DBDebugUtils import DBDebugDA
from secdaily._00_common.ParallelExecution import ParallelExecutor
from secdaily._00_common.SecFileUtils import read_content_from_zip, read_df_from_zip
from secdaily._02_xml.db.XmlFileParsingDataAccess import UnparsedFile, UpdatePreParsing
from secdaily._02_xml.SecXmlFileParsing import SecXmlParser


class DataAccessTool:
    def __init__(self, workdir="./"):
        if workdir[-1] != "/":
            workdir = workdir + "/"

        self.workdir = workdir
        self.qtrdir = workdir + "quarterzip/"
        self.dailyzipdir = workdir + "daily/"
        self.dbmgr = DBDebugDA(workdir)

    def _read_file_from_zip(self, zipfile_to_read: str, file_to_read: str, read_as_str=False) -> pd.DataFrame:
        with zipfile.ZipFile(zipfile_to_read, "r") as myzip:
            if read_as_str:
                return pd.read_csv(myzip.open(file_to_read), header=0, delimiter="\t", dtype=str)
            return pd.read_csv(myzip.open(file_to_read), header=0, delimiter="\t", dtype=str)

    def _get_zipfilename(self, year: int, qrtr: int) -> str:
        return self.qtrdir + str(year) + "q" + str(qrtr) + ".zip"

    def _get_by_adsh_from_quarter(self, year: int, qrtr: int, adsh: str, file: str) -> pd.DataFrame:
        "file is num.txt, pre.txt or sub.txt"
        zipfilename = self._get_zipfilename(year, qrtr)
        df = self._read_file_from_zip(zipfilename, file)
        return df[df.adsh == adsh].copy()

    def get_pre_by_adsh_from_quarter(self, year: int, qrtr: int, adsh: str) -> pd.DataFrame:
        return self._get_by_adsh_from_quarter(year, qrtr, adsh, "pre.txt")

    def get_num_by_adsh_from_quarter(self, year: int, qrtr: int, adsh: str) -> pd.DataFrame:
        return self._get_by_adsh_from_quarter(year, qrtr, adsh, "num.txt")

    def get_sub_by_adsh_from_quarter(self, year: int, qrtr: int, adsh: str) -> pd.DataFrame:
        return self._get_by_adsh_from_quarter(year, qrtr, adsh, "sub.txt")

    def get_pre_xml_content_by_adsh(self, adsh: str):
        adsh, xmlpre, _, _, _ = self.dbmgr.get_files_for_adsh(adsh)
        return read_content_from_zip(xmlpre)

    def get_num_xml_content_by_adsh(self, adsh: str):
        adsh, _, xmlnum, _, _ = self.dbmgr.get_files_for_adsh(adsh)
        return read_content_from_zip(xmlnum)

    def get_pre_csv_as_df_by_adsh(self, adsh: str) -> pd.DataFrame:
        adsh, _, _, csvpre, _ = self.dbmgr.get_files_for_adsh(adsh)
        return read_df_from_zip(csvpre)

    def get_num_csv_as_df_by_adsh(self, adsh: str) -> pd.DataFrame:
        adsh, _, _, _, csvnum = self.dbmgr.get_files_for_adsh(adsh)
        return read_df_from_zip(csvnum)


class DataAccessByAdshTool:

    def __init__(self, workdir: str, adsh: str, year: int, qrtr: int):
        self.tool = DataAccessTool(workdir)
        self.adsh = adsh
        self.year = year
        self.qrtr = qrtr

    def get_pre_from_qrtr_zip(self) -> pd.DataFrame:
        return self.tool.get_pre_by_adsh_from_quarter(self.year, self.qrtr, self.adsh)

    def get_num_from_qrtr_zip(self) -> pd.DataFrame:
        return self.tool.get_num_by_adsh_from_quarter(self.year, self.qrtr, self.adsh)

    def get_pre_xml_content(self) -> str:
        return self.tool.get_pre_xml_content_by_adsh(self.adsh)

    def get_num_xml_content(self) -> str:
        return self.tool.get_num_xml_content_by_adsh(self.adsh)

    def get_pre_csv_as_df(self) -> pd.DataFrame:
        return self.tool.get_pre_csv_as_df_by_adsh(self.adsh)

    def get_num_csv_as_df(self) -> pd.DataFrame:
        return self.tool.get_num_csv_as_df_by_adsh(self.adsh)


class TestSetCreatorTool:
    def __init__(self, workdir: str):
        self.tool = DataAccessTool(workdir)

    def get_testset_by_year_and_months(self, year: int, months: List[int], count: Optional[int] = None) -> List[str]:
        conn = self.tool.dbmgr.get_connection()
        months_str = ",".join([str(month) for month in months])

        try:
            sql = f"""SELECT accessionNumber
                      FROM sec_report_processing
                      WHERE filingYear = {year} AND filingMonth in ({months_str})
                            AND xmlPreFile not null AND xmlNumFile not null order by accessionNumber """
            selection: List[Tuple[str]] = conn.execute(sql).fetchall()
            result: List[str] = [x[0] for x in selection]
            if count is not None:
                return result[:count]
            return result
        finally:
            conn.close()

    def get_daily_zips_by_year_and_montsh(self, year: int, months: List[int], count: Optional[int] = None) -> List[str]:

        conn = self.tool.dbmgr.get_connection()
        months_str = ",".join([str(month) for month in months])

        try:
            sql = f"""SELECT DISTINCT dailyZipFile
                      FROM sec_report_processing
                      WHERE filingYear = {year} and filingMonth in ({months_str})"""
            selection: List[Tuple[str]] = conn.execute(sql).fetchall()
            result: List[str] = [x[0] for x in selection]
            if count is not None:
                return result[:count]
            return result
        finally:
            conn.close()


class ReparseTool:

    def __init__(self, workdir: str):
        self.tool = DataAccessTool(workdir)

    def reparse_pre_by_adshs(
        self,
        adshs: List[str],
        targetFolder: str,
    ):
        xml_files_info: List[Tuple[str, str, str]] = self.tool.dbmgr.get_xml_files_info_from_sec_processing_by_adshs(
            adshs
        )
        pre_xml_files_info: List[Tuple[str, str]] = [(x[0], x[2]) for x in xml_files_info]  # adsh and preXmlFile

        def select_funct():
            return pre_xml_files_info

        def update_function(data: List[UpdatePreParsing]):
            for entry in data:
                print(entry)

        # tbd: check if correctly changed
        xmlParser = SecXmlParser(None, targetFolder)

        executor = ParallelExecutor[UnparsedFile, UpdatePreParsing, type(None)]()  # no limitation in speed

        executor.set_get_entries_function(select_funct)
        executor.set_process_element_function(xmlParser._parse_pre_file) # pylint: disable=protected-access
        executor.set_post_process_chunk_function(update_function)

        executor.execute()


if __name__ == "__main__":
    # short test to check if all methods can be executed
    adsh_tool = DataAccessByAdshTool("d:/secprocessing/", "0001437749-21-005151", 2021, 1)
    adsh_tool.get_pre_from_qrtr_zip()
    adsh_tool.get_num_from_qrtr_zip()
    adsh_tool.get_pre_xml_content()
    adsh_tool.get_num_xml_content()
    adsh_tool.get_pre_csv_as_df()
    adsh_tool.get_num_csv_as_df()
