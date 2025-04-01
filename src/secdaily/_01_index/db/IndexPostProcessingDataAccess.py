from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from secdaily._00_common.DBBase import DB


@dataclass
class XbrlFile:
    name: str
    url: str
    lastChange: str
    size: int

    @staticmethod
    def default() -> 'XbrlFile':
        return XbrlFile(name="", url="", lastChange="", size=0)


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


class IndexPostProcessingDA(DB):

    def read_last_known_fiscalyearend(self) -> Dict[str, str]:
        sql = '''
        SELECT cikNumber, fiscalYearEnd 
        FROM (
             SELECT cikNumber, fiscalYearEnd 
             FROM {} 
             WHERE formType = "10-K" and fiscalYearEnd is not null 
             ORDER BY cikNumber, period desc
             ) as x 
        GROUP BY cikNumber;
        '''.format(DB.SEC_REPORTS_TBL_NAME)
        # return as dict, where cikNumber is the key and the fiscalYearEnd is the value
        df = self._execute_read_as_df(sql)
        return df.set_index('cikNumber')['fiscalYearEnd'].to_dict()

    def find_entries_with_missing_xbrl_ins_or_pre(self) -> List[BasicFeedData]:
        sql = '''SELECT accessionNumber, sec_feed_file, formType, cikNumber, reportJson FROM {} WHERE xbrlInsUrl is NULL OR xbrlPreUrl is NULL'''.format(
            DB.SEC_REPORTS_TBL_NAME)
        return self._execute_fetchall_typed(sql, BasicFeedData)

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
                 WHERE accessionNumber = ? and sec_feed_file = ?'''.format(DB.SEC_REPORTS_TBL_NAME)
        self._execute_many(sql, update_data)

    def find_duplicated_adsh(self) -> List[str]:
        sql = '''SELECT COUNT(*) as mycount, accessionNumber FROM {} WHERE status is null GROUP BY accessionNumber'''.format(
            DB.SEC_REPORTS_TBL_NAME)
        duplicated_df = self._execute_read_as_df(sql)

        duplicated_df = duplicated_df[duplicated_df.mycount > 1].copy()
        return duplicated_df.accessionNumber.tolist()

    def mark_duplicated_adsh(self, adsh: str):
        sql = '''SELECT accessionNumber, sec_feed_file FROM {} WHERE accessionNumber= '{}' and status is null order by sec_feed_file'''.format(
            DB.SEC_REPORTS_TBL_NAME, adsh)
        result: List[Tuple[str]] = self._execute_fetchall(sql)

        update_sql = '''UPDATE {} SET status = 'duplicated' WHERE accessionNumber = ? and sec_feed_file = ? '''.format(
            DB.SEC_REPORTS_TBL_NAME)
        self._execute_many(update_sql, result[1:])
