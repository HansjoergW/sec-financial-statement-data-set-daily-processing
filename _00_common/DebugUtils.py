from _00_common.DBManagement import DBManager

import pandas as pd
import zipfile

class Tools():
    def __init__(self, workdir = './'):
        if workdir[-1] != '/':
            data_dir = workdir + '/'

        self.workdir = workdir
        self.qtrdir = workdir + 'quarterzip/'
        self.dbmgr = DBManager(workdir)

    def _read_file_from_zip(self, zipfile_to_read: str, file_to_read: str) -> pd.DataFrame:
        with zipfile.ZipFile(zipfile_to_read, "r") as myzip:
            return pd.read_csv(myzip.open(file_to_read), header=0, delimiter="\t")

    def _get_zipfilename(self,  year: int, qrtr: int) -> str:
        return self.qtrdir + str(year)+ 'q' + str(qrtr) + '.zip'

    def _get_by_adsh_from_quarter(self, year: int, qrtr: int, adsh: str, file: str) -> pd.DataFrame:
        "file is num.txt, pre.txt or sub.txt"
        zipfilename = self._get_zipfilename(year, qrtr)
        df = self._read_file_from_zip(zipfilename, file)
        return df[df.adsh == adsh].copy()

    def get_pre_by_adsh_from_quarter(self, year: int, qrtr: int, adsh: str) -> pd.DataFrame:
        return self._get_by_adsh_from_quarter(year, qrtr, adsh, "pre.txt")

    def get_num_by_adsh_from_quarter(self, year: int, qrtr: int, adsh: str) -> pd.DataFrame:
        return self._get_by_adsh_from_quarter(year, qrtr, adsh, "num.txt")

    def get_pre_xml_content_by_adsh(self, adsh: str):
        adsh, xmlpre, xmlnum, csvpre, csvnum = self.dbmgr.get_files_for_adsh(adsh)
        with open(xmlpre, "r", encoding="utf-8") as f:
            return f.read()

    def get_num_xml_content_by_adsh(self, adsh: str):
        adsh, xmlpre, xmlnum, csvpre, csvnum = self.dbmgr.get_files_for_adsh(adsh)
        with open(xmlnum, "r", encoding="utf-8") as f:
            return f.read()

    def get_pre_csv_as_df_by_adsh(self, adsh: str) -> pd.DataFrame:
        adsh, xmlpre, xmlnum, csvpre, csvnum = self.dbmgr.get_files_for_adsh(adsh)
        return pd.read_csv(csvpre, header=0, delimiter="\t")

    def get_num_csv_as_df_by_adsh(self, adsh: str) -> pd.DataFrame:
        adsh, xmlpre, xmlnum, csvpre, csvnum = self.dbmgr.get_files_for_adsh(adsh)
        return pd.read_csv(csvnum, header=0, delimiter="\t")


class AdshTool():

    def __init__(self, workdir: str, adsh: str, year: int, qrtr: int):
        self.tool = Tools(workdir)
        self.adsh = adsh
        self.year = year
        self.qrtr = qrtr

    def get_pre_from_qrtr_zip(self) -> pd.DataFrame:
        return self.tool.get_pre_by_adsh_from_quarter(self.year, self. qrtr, self.adsh)

    def get_num_from_qrtr_zip(self) -> pd.DataFrame:
        return self.tool.get_num_by_adsh_from_quarter(self.year, self. qrtr, self.adsh)

    def get_pre_xml_content(self) -> str:
        return self.tool.get_pre_xml_content_by_adsh(self.adsh)

    def get_num_xml_content(self) -> str:
        return self.tool.get_num_xml_content_by_adsh(self.adsh)

    def get_pre_csv_as_df(self) -> pd.DataFrame:
        return self.tool.get_pre_csv_as_df_by_adsh(self.adsh)

    def get_num_csv_as_df(self) -> pd.DataFrame:
        return self.tool.get_num_csv_as_df_by_adsh(self.adsh)



if __name__ == '__main__':
    adsh_tool = AdshTool("d:/secprocessing/", '0001437749-21-005151', 2021, 1)
    adsh_tool.get_pre_from_qrtr_zip()
    adsh_tool.get_num_from_qrtr_zip()
    adsh_tool.get_pre_xml_content()
    adsh_tool.get_num_xml_content()
    adsh_tool.get_pre_csv_as_df()
    adsh_tool.get_num_csv_as_df()

