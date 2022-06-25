from _00_common.DBBase import DB
from dataclasses import dataclass
from typing import List, Tuple, Set, Optional, Dict

import pandas as pd


@dataclass
class XbrlFile:
    name: str
    url: str
    lastChange: str
    size: int


@dataclass
class XbrlFiles:
    accessionNumber: str
    sec_feed_file: str
    fiscal_year_end: Optional[str]
    period: Optional[str]
    xbrlIns: Optional[XbrlFile]
    xbrlPre: Optional[XbrlFile]
    xbrlCal: Optional[XbrlFile]
    xbrlDef: Optional[XbrlFile]
    xbrlLab: Optional[XbrlFile]
    xbrlZip: Optional[XbrlFile]


@dataclass
class BasicFeedData:
    accessionNumber: str
    sec_feed_file: str
    formType: str
    cikNumber: str
    reportJson: str


@dataclass
class UpdateNumParsing:
    accessionNumber: str
    csvNumFile: Optional[str]
    numParseDate: str
    numParseState: str
    fiscalYearEnd: Optional[str]


@dataclass
class UpdatePreParsing:
    accessionNumber: str
    csvPreFile: Optional[str]
    preParseDate: str
    preParseState: str


@dataclass
class MissingFile:
    accessionNumber: str
    url: str
    fileSize: str
    file: Optional[str] = None


@dataclass
class UnparsedFile:
    accessionNumber: str
    file: str


# noinspection SqlResolve
class DBManager(DB):

    def __init__(self, work_dir="edgar/"):
        super().__init__(work_dir)

    # ---- fullindex files ----
    def read_all_fullindex_files(self) -> pd.DataFrame:
        sql = '''SELECT * FROM {}'''.format(DB.SEC_FULL_INDEX_FILE_TBL_NAME)
        return self._execute_read_as_df(sql)

    def insert_fullindex_file(self, year: int, qrtr: int, processdate: str):
        sql = '''INSERT INTO {} ('year', 'quarter', 'processdate') VALUES({}, {}, '{}') '''.format(
            DB.SEC_FULL_INDEX_FILE_TBL_NAME, year, qrtr, processdate)
        self._execute_single(sql)

    def update_fullindex_file(self, year: int, qrtr: int, processdate: str):
        sql = '''UPDATE {} SET 'processdate' = '{}' WHERE  year == {} AND quarter == {}  '''.format(
            DB.SEC_FULL_INDEX_FILE_TBL_NAME, processdate, year, qrtr)
        self._execute_single(sql)

    def update_status_fullindex_file(self, year: int, qrtr: int, status: str):
        sql = '''UPDATE {} SET 'state' = '{}' WHERE  year == {} AND quarter == {} '''.format(
            DB.SEC_FULL_INDEX_FILE_TBL_NAME, status, year, qrtr)
        self._execute_single(sql)

    # ---- index files / sec-feed-file table
    def read_all_index_files(self) -> pd.DataFrame:
        sql = '''SELECT * FROM {}'''.format(DB.SEC_INDEX_FILE_TBL_NAME)
        return self._execute_read_as_df(sql)

    def insert_index_file(self, name: str, processdate: str):
        sql = '''INSERT INTO {} ('sec_feed_file', 'processdate') VALUES('{}','{}') '''.format(DB.SEC_INDEX_FILE_TBL_NAME,
                                                                                              name, processdate)
        self._execute_single(sql)

    def update_index_file(self, name: str, processdate: str):
        sql = '''UPDATE {} SET 'processdate' = '{}' WHERE  sec_feed_file == '{}' '''.format(DB.SEC_INDEX_FILE_TBL_NAME,
                                                                                            processdate, name)
        self._execute_single(sql)

    def update_status_index_file(self, name: str, status: str):
        sql = '''UPDATE {} SET 'status' = '{}' WHERE  sec_feed_file == '{}' '''.format(DB.SEC_INDEX_FILE_TBL_NAME, status,
                                                                                       name)
        self._execute_single(sql)

    # - processing file / sec-report-processing table
    def read_all_processing(self) -> pd.DataFrame:
        sql = '''SELECT * FROM {}'''.format(DB.SEC_REPORT_PROCESSING_TBL_NAME)
        return self._execute_read_as_df(sql)

    def get_xml_files_info_from_sec_processing_by_adshs(self, adshs: List[str]) -> List[Tuple[str, str, str]]:
        conn = self.get_connection()
        adshs = ','.join("'" + adsh + "'" for adsh in adshs)

        sql = '''SELECT accessionNumber, xmlNumFile, xmlPreFile from sec_report_processing WHERE accessionNumber in ({}) and xmlPreFile not null and xmlNumFile not null order by accessionNumber '''.format(
            adshs)
        return self._execute_fetchall(sql)

    def get_files_for_adsh(self, adsh: str) -> Tuple[str, str, str, str, str]:
        conn = self.get_connection()
        try:
            sql = '''SELECT accessionNumber, xmlPreFile, xmlNumFile, csvPreFile, csvNumFile FROM {} where accessionNumber = '{}' '''.format(
                DB.SEC_REPORT_PROCESSING_TBL_NAME, adsh)
            return conn.execute(sql).fetchone()  # !! Attention: fetchone !!
        finally:
            conn.close()

    def find_missing_xmlNumFiles(self) -> List[MissingFile]:
        sql = '''SELECT accessionNumber, xbrlInsUrl as url, insSize as fileSize FROM {} WHERE xmlNumFile is NULL'''.format(
            DB.SEC_REPORT_PROCESSING_TBL_NAME)
        return self._execute_fetchall_typed(sql, MissingFile)

    def find_missing_xmlPreFiles(self) -> List[MissingFile]:
        sql = '''SELECT accessionNumber, xbrlPreUrl as url, preSize as fileSize FROM {} WHERE xmlPreFile is NULL'''.format(
            DB.SEC_REPORT_PROCESSING_TBL_NAME)
        return self._execute_fetchall_typed(sql, MissingFile)

    def update_processing_xml_num_file(self, update_list: List[MissingFile]):
        update_data = [(x.file, x.accessionNumber) for x in update_list]
        sql = '''UPDATE {} SET xmlNumFile = ? WHERE accessionNumber = ?'''.format(DB.SEC_REPORT_PROCESSING_TBL_NAME)
        self._execute_many(sql, update_data)

    def update_processing_xml_pre_file(self, update_list: List[MissingFile]):
        update_data = [(x.file, x.accessionNumber) for x in update_list]
        sql = '''UPDATE {} SET xmlPreFile = ? WHERE accessionNumber = ?'''.format(DB.SEC_REPORT_PROCESSING_TBL_NAME)
        self._execute_many(sql, update_data)

    def find_unparsed_numFiles(self) -> List[UnparsedFile]:
        sql = '''SELECT accessionNumber, xmlNumFile as file FROM {} WHERE csvNumFile is NULL and numParseState is NULL'''.format(
            DB.SEC_REPORT_PROCESSING_TBL_NAME)
        return self._execute_fetchall_typed(sql, UnparsedFile)

    def find_unparsed_preFiles(self) -> List[Tuple[str, str]]:
        sql = '''SELECT accessionNumber, xmlPreFile as file FROM {} WHERE csvPreFile is NULL and preParseState is NULL'''.format(
            DB.SEC_REPORT_PROCESSING_TBL_NAME)
        return self._execute_fetchall_typed(sql, UnparsedFile)

    def update_parsed_num_file(self, updatelist: List[UpdateNumParsing]):
        update_data = [(x.csvNumFile, x.numParseDate, x.numParseState, x.fiscalYearEnd, x.accessionNumber) for x in
                       updatelist]

        sql = '''UPDATE {} SET csvNumFile = ?, numParseDate = ?, numParseState = ?, fiscalYearEnd =? WHERE accessionNumber = ?'''.format(
            DB.SEC_REPORT_PROCESSING_TBL_NAME)
        self._execute_many(sql, update_data)

    def update_parsed_pre_file(self, updatelist: List[UpdatePreParsing]):
        update_data = [(x.csvPreFile, x.preParseDate, x.preParseState, x.accessionNumber) for x in updatelist]

        sql = '''UPDATE {} SET csvPreFile = ?, preParseDate = ?, preParseState = ? WHERE accessionNumber = ?'''.format(
            DB.SEC_REPORT_PROCESSING_TBL_NAME)
        self._execute_many(sql, update_data)

    def find_ready_to_zip_adshs(self) -> pd.DataFrame:
        conn = self.get_connection()
        try:
            # select days which have entries that are not in a daily zip file
            sql = '''SELECT DISTINCT filingDate FROM {} WHERE preParseState like "parsed%" and numParseState like "parsed%" and processZipDate is NULL'''.format(
                DB.SEC_REPORT_PROCESSING_TBL_NAME)
            datesToZip_result: List[Tuple[str]] = conn.execute(sql).fetchall()
            datesToZip: List[str] = [dateToZip[0] for dateToZip in datesToZip_result]
            zipdates = ','.join("'" + zipdate + "'" for zipdate in datesToZip)

            # select all entries which belong to the found zipdates above
            sql = '''SELECT accessionNumber, filingDate, csvPreFile, csvNumfile, fiscalYearEnd FROM {} WHERE preParseState like "parsed%" and numParseState like "parsed%" and filingDate in({}) '''.format(
                DB.SEC_REPORT_PROCESSING_TBL_NAME, zipdates)
            return pd.read_sql_query(sql, conn)
        finally:
            conn.close()

    def updated_ziped_entries(self, update_data: List[Tuple[str, str, str]]):
        sql = '''UPDATE {} SET dailyZipFile = ?, processZipDate = ? WHERE accessionNumber = ?'''.format(
            DB.SEC_REPORT_PROCESSING_TBL_NAME)
        self._execute_many(sql, update_data)

    # - report metadata / sec-feed table
    def read_all(self) -> pd.DataFrame:
        sql = '''SELECT * FROM {}'''.format(DB.SEC_FEED_TBL_NAME)
        return self._execute_read_as_df(sql)

    def read_last_known_fiscalyearend(self) -> Dict[str, str]:
        sql = '''
        SELECT cikNumber, fiscalYearEnd 
        FROM (
             SELECT cikNumber, fiscalYearEnd 
             FROM sec_feeds 
             WHERE formType = "10-K" and fiscalYearEnd is not null 
             ORDER BY cikNumber, period desc
             ) as x 
        GROUP BY cikNumber;
        '''
        # return as dict, where cikNumber is the key and the fiscalYearEnd is the value
        df = self._execute_read_as_df(sql)
        return df.set_index('cikNumber')['fiscalYearEnd'].to_dict()

    def read_by_year_and_quarter(self, year: int, qrtr: int) -> pd.DataFrame:
        months: List = [1, 2, 3]
        offset = ((qrtr - 1) * 3)
        months = [str(x + offset) for x in months]
        month_str = ",".join(months)

        sql = '''SELECT * FROM {} WHERE filingYear = {} and filingMonth in ({})  '''.format(DB.SEC_FEED_TBL_NAME, year,
                                                                                            month_str)
        return self._execute_read_as_df(sql)

    def read_all_copied(self) -> pd.DataFrame:
        sql = '''SELECT * FROM {} WHERE status is 'copied' '''.format(DB.SEC_FEED_TBL_NAME)
        return self._execute_read_as_df(sql)

    def insert_feed_info(self, df: pd.DataFrame):
        conn = self.get_connection()
        try:
            df.to_sql(DB.SEC_FEED_TBL_NAME, conn, if_exists="append", chunksize=1000)
        finally:
            conn.close()

    def find_entries_with_missing_xbrl_ins_or_pre(self) -> List[BasicFeedData]:
        sql = '''SELECT accessionNumber, sec_feed_file, formType, cikNumber, reportJson FROM {} WHERE xbrlInsUrl is NULL OR xbrlPreUrl is NULL'''.format(
            DB.SEC_FEED_TBL_NAME)
        return self._execute_fetchall_typed(sql, BasicFeedData)

    def find_missing_xbrl_ins_urls(self) -> List[Tuple[str]]:
        sql = '''SELECT accessionNumber, xbrlInsUrl, xbrlPreUrl FROM {} WHERE xbrlInsUrl is NULL'''.format(
            DB.SEC_FEED_TBL_NAME)
        return self._execute_fetchall(sql)

    def update_xbrl_infos(self, xbrlfiles: List[XbrlFiles]):

        def expand(info: XbrlFile):
            if info is None:
                return (None, None, None)
            return (info.url, info.lastChange, info.size)

        update_data = [
            (file.period,
             file.fiscal_year_end,
             *expand(file.xbrlIns),
             *expand(file.xbrlCal),
             *expand(file.xbrlLab),
             *expand(file.xbrlDef),
             *expand(file.xbrlPre),
             *expand(file.xbrlZip),
             file.accessionNumber,
             file.sec_feed_file
             )
            for file in xbrlfiles
        ]

        sql = '''UPDATE {} SET  period = ?,
                                fiscalYearEnd = ?, 
                                xbrlInsUrl = ?, insLastChange = ?, insSize = ?, 
                                xbrlCalUrl = ?, calLastChange = ?, calSize = ?,
                                xbrlLabUrl = ?, labLastChange = ?, labSize = ?,
                                xbrlDefUrl = ?, defLastChange = ?, defSize = ?,
                                xbrlPreUrl = ?, preLastChange = ?, preSize = ?,
                                xbrlZipUrl = ?, zipLastChange = ?, zipSize = ?
                 WHERE accessionNumber = ? and sec_feed_file = ?'''.format(DB.SEC_FEED_TBL_NAME)
        self._execute_many(sql, update_data)

    # TODO: korrekterweise muesste man hier die WHERE neu zusätzlich mit sec_feed_file ergänzen
    def update_xbrl_ins_urls(self, update_data: List[Tuple[str, str, str]]):
        sql = '''UPDATE {} SET xbrlInsUrl = ?, insSize = ? WHERE accessionNumber = ?'''.format(DB.SEC_FEED_TBL_NAME)
        self._execute_many(sql, update_data)

    def get_adsh_by_feed_file(self, feed_file_name: str) -> Set[str]:
        sql = '''SELECT accessionNumber FROM sec_feeds where sec_feed_file == '{}' '''.format(feed_file_name)
        result: List[Tuple[str]] = self._execute_fetchall(sql)
        return set([x[0] for x in result])

    def find_duplicated_adsh(self) -> List[str]:
        sql = '''SELECT COUNT(*) as mycount, accessionNumber FROM sec_feeds WHERE status is null GROUP BY accessionNumber'''
        duplicated_df = self._execute_read_as_df(sql)

        duplicated_df = duplicated_df[duplicated_df.mycount > 1].copy()
        return duplicated_df.accessionNumber.tolist()

    def mark_duplicated_adsh(self, adsh: str):
        sql = '''SELECT accessionNumber, sec_feed_file FROM sec_feeds WHERE accessionNumber= '{}' and status is null order by sec_feed_file'''.format(
            adsh)
        result: List[Tuple[str]] = self._execute_fetchall(sql)

        update_sql = '''UPDATE {} SET status = 'duplicated' WHERE accessionNumber = ? and sec_feed_file = ? '''.format(
            DB.SEC_FEED_TBL_NAME)
        self._execute_many(update_sql, result[1:])

    # copies entries from the feed table to the processing table if they are not already present
    def copy_uncopied_entries(self) -> int:
        sql = '''SELECT accessionNumber, cikNumber, filingDate, formType, xbrlInsUrl, insSize, xbrlPreUrl, preSize  FROM sec_feeds WHERE status is null and xbrlInsUrl is not null'''
        to_copy_df = self._execute_read_as_df(sql)

        to_copy_df['filingMonth'] = pd.to_numeric(to_copy_df.filingDate.str.slice(0, 2), downcast="integer")
        to_copy_df['filingDay'] = pd.to_numeric(to_copy_df.filingDate.str.slice(3, 5), downcast="integer")
        to_copy_df['filingYear'] = pd.to_numeric(to_copy_df.filingDate.str.slice(6, 10), downcast="integer")

        conn = self.get_connection()
        try:
            to_copy_df.to_sql(DB.SEC_REPORT_PROCESSING_TBL_NAME, conn, index=False, if_exists="append", chunksize=1000)

            update_sql = '''UPDATE {} SET status = 'copied' WHERE accessionNumber = ? and status is null '''.format(
                DB.SEC_FEED_TBL_NAME)
            adshs = to_copy_df.accessionNumber.values.tolist()
            tupleslist = [tuple(x.split()) for x in adshs]

            conn.executemany(update_sql, tupleslist)

            conn.commit()
            return len(to_copy_df)
        finally:
            conn.close()

