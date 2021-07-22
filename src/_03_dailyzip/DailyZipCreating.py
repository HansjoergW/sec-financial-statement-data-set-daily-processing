from _00_common.DBManagement import DBManager
from _00_common.SecFileUtils import read_df_from_zip
from typing import List, Tuple
from multiprocessing import Pool

import pandas as pd
import numpy as np
import zipfile
import math
import os
import datetime
import logging

class DailyZipCreator:

    def __init__(self, dbmanager: DBManager, daily_zip_dir: str = "./tmp/daily/"):
        self.dbmanager = dbmanager

        if daily_zip_dir[-1] != '/':
            daily_zip_dir = daily_zip_dir + '/'

        self.daily_zip_dir = daily_zip_dir
        self.processdate = datetime.date.today().isoformat()

    def _read_ready_entries(self) -> pd.DataFrame:
        return self.dbmanager.find_ready_to_zip_adshs()

    def _read_feed_entries_for_adshs(self, adshs: List[str]) -> pd.DataFrame:
        feed_entries = self.dbmanager.read_all_copied()
        feed_entries = feed_entries[feed_entries.accessionNumber.isin(adshs)]
        return self._process_df(feed_entries)

    def _process_df(self, df: pd.DataFrame) -> pd.DataFrame:
        # adsh:     edgar:accessionNumber
        # cik:      edgar:cikNumber	/ no leading zeros
        # name:     edgar:companyName	/ upper case
        # sic:      edgar:assignedSic

        # form:     edgar:formType
        # period:   edgar:period
        # fye:      edgar:fiscalYearEnd	 / MMDD /  "with leading zero / 0228 ->rounded to 0229 in leap year
        # fy:       "actual year for 10K /year for next 10K"
        # fp:       "FY for 10K / actual Quarter"
        # filed:    edgar:fillingDate yyyyMMdd
        # accepted: edgar:acceptanceDatetime /	"like: 20210107161557 / rounded to minutes"

        sub_entries = df[['accessionNumber','cikNumber', 'companyName','assignedSic','fiscalYearEnd','formType','period','filingDate','acceptanceDatetime']].copy()

        # rename to sub-file column names
        sub_entries.rename(columns = {'accessionNumber': 'adsh',
                                      'cikNumber': 'cik',
                                      'companyName': 'name',
                                      'assignedSic': 'sic',
                                      'fiscalYearEnd': 'fye',
                                      'formType': 'form',
                                      'filingDate': 'filed',
                                      'acceptanceDatetime': 'accepted'}, inplace=True)

        if len(sub_entries) == 0:
            return sub_entries

        # simple conversions
        sub_entries['cik'] = sub_entries.cik.astype(int)
        sub_entries['name'] = sub_entries.name.str.upper()
        sub_entries['name'] = sub_entries.name.str.replace('\\','', regex=False)


        # check for Null Values in fye
        # there are some entries, which don't have a fye entry. if it is a 10-k, then this is the month and year of period
        sub_entries.loc[sub_entries.fye.isnull() & (sub_entries.form == '10-K'), 'fye'] = sub_entries.period.str.slice(4,8)
        # if it is a 10-q, we cannot say...
        sub_entries.loc[sub_entries.fye.isnull(), 'fye'] = "0000"

        # create helper columns
        sub_entries['period_date'] = pd.to_datetime(sub_entries.period, format='%Y%m%d')
        sub_entries['period_year'] = sub_entries.period.str.slice(0,4).astype(int)
        sub_entries['period_month'] = sub_entries.period.str.slice(4,6).astype(int)
        sub_entries['period_day'] = sub_entries.period.str.slice(6,8).astype(int)

        # round period to end of date
        mask = (sub_entries.period_day <= 15) | ((sub_entries.period_day == 16) & sub_entries.period_month.isin([1,3,5,7,8,10,12]))
        sub_entries.loc[mask,'period_date'] = sub_entries.period_date - pd.DateOffset(months=1)
        sub_entries['period'] = sub_entries.period_date.dt.to_period('M').dt.to_timestamp('M').dt.strftime('%Y%m%d')

        sub_entries['fye_month'] = sub_entries.fye.str.slice(0,2).astype(int)
        sub_entries['fye_day'] = sub_entries.fye.str.slice(2,4).astype(int)

        # sollten immer ende monat sein, fye muss deshalb noch korrigiert werden. Es gibt die funkction map in dataframes, die das relativ einfach lösen könnte
        #
        # https://stackoverflow.com/questions/20250771/remap-values-in-pandas-column-with-a-dict

        month_end = {0:0, 1: 31, 2: 28, 3:31, 4: 30, 5: 31, 6:30, 7:31, 8:31, 9:30, 10: 31, 11: 30, 12: 31}
        sub_entries['fye_day'] = sub_entries.fye_month.map(month_end)
        sub_entries['fye'] = sub_entries.fye_month * 100 + sub_entries.fye_day
        sub_entries['fye'] = sub_entries.fye.astype(str).str.zfill(4)

        # correction for 29 of feb in order to not run into problems later on
        sub_entries.loc[(sub_entries.fye_month==2) & (sub_entries.fye_day==29), 'fye_day'] = 28

        sub_entries['is_fye_same_year'] = (sub_entries.form == '10-K') | ((sub_entries.fye_month*100+sub_entries.fye_day) >= (sub_entries.period_month*100+sub_entries.period_day))

        # fy
        sub_entries.loc[sub_entries.is_fye_same_year,'fy'] = sub_entries.period_year
        sub_entries.loc[sub_entries.is_fye_same_year == False,'fy'] = sub_entries.period_year + 1
        sub_entries.fy = sub_entries.fy.astype(int)

        sub_entries.loc[sub_entries.fye == '0000','fy'] = 0 # cannot be calculated, if there was no fye entry

        # fp
        #  date when the last fiscal year ended
        sub_entries['fye_date_prev'] = pd.to_datetime((sub_entries.fy - 1 ) *10000+sub_entries.fye_month*100+sub_entries.fye_day, format='%Y%m%d', errors='coerce')

        sub_entries['fye_period_diff'] = 0

        sub_entries.loc[sub_entries.fye != '0000', 'fye_period_diff'] = (sub_entries.period_date - sub_entries.fye_date_prev) / np.timedelta64(1,'D')

        sub_entries.loc[sub_entries.form == '10-K','fp'] = 'FY'
        sub_entries.loc[sub_entries.form != '10-K' ,'fp'] = 'Q' + (sub_entries.fye_period_diff / 91.5).round().astype(str).str.slice(0,1)
        sub_entries.loc[sub_entries.fye == '0000','fp'] = 'Q0' # cannot be calculated, if there was no fye entry
        

        #  07/01/2021-> 20210107
        sub_entries['filed'] = pd.to_datetime(sub_entries.filed, format='%m/%d/%Y')
        sub_entries['filed'] = sub_entries.filed.dt.strftime('%Y%m%d')

        # accepted -> 20210107161557 rounded to minutes
        # 20210107132023-> 07.01.2021 13:20:00.0
        sub_entries['accepted'] = pd.to_datetime(sub_entries.accepted, format='%Y%m%d%H%M%S')
        sub_entries['accepted'] = sub_entries.accepted.dt.round('min')
        sub_entries['accepted'] = sub_entries.accepted.dt.strftime('%Y-%m-%d %H:%M:00.0')

        # drop helper columns
        sub_entries.drop(columns=['period_year', 'period_month', 'period_day', 'fye_month',
                                  'fye_day', 'is_fye_same_year', 'fye_date_prev', 'period_date', 'fye_period_diff'], inplace=True)

        return sub_entries

    def _read_csvfiles(self, filelist: List[str]) -> str:
        dfs = [read_df_from_zip(file) for file in filelist]
        return pd.concat(dfs).to_csv(sep="\t", header=True, index=False)

    def _create_daily_content(self, date:str, entries: pd.DataFrame, entries_sub_df: pd.DataFrame)-> Tuple[str, str, str]:
        sub_content = entries_sub_df.to_csv(sep="\t", header=True, index=False)
        pre_content = self._read_csvfiles(entries.csvPreFile.tolist())
        num_content = self._read_csvfiles(entries.csvNumFile.tolist())
        return sub_content, pre_content, num_content

    def _get_qrtr(self, filing_date: str) -> str:
        year = filing_date[6:]
        month = filing_date[0:2]
        month_int = int(month)
        qtr = math.floor((month_int - 1) / 3) + 1

        return year + "q" + str(qtr)

    def _store_to_zip(self, filing_date: str, sub: str, pre: str, num: str) -> str:
        qrtr = self._get_qrtr(filing_date)
        qtr_dir = os.path.join(self.daily_zip_dir, qrtr)
        os.makedirs(os.path.join(qtr_dir), exist_ok=True)

        year = filing_date[6:]
        month = filing_date[0:2]
        day = filing_date[3:5]
        zipfile_name = year+month+day+".zip"
        zipfile_path = os.path.join(qtr_dir, zipfile_name)
        with zipfile.ZipFile(zipfile_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('sub.txt', sub)
            zf.writestr('pre.txt', pre)
            zf.writestr('num.txt', num)

        return zipfile_name

    def _process_date(self, data: Tuple[str, pd.DataFrame, pd.DataFrame]):
        filing_date: str = data[0]
        group_df: pd.DataFrame = data[1]
        entries_sub: pd.DataFrame = data[2]

        try:
            adshs = group_df.accessionNumber.tolist()
            sub, pre, num = self._create_daily_content(filing_date, group_df, entries_sub[entries_sub.adsh.isin(adshs)])
            zf_name = self._store_to_zip(filing_date, sub,pre, num)
            update_data = [(zf_name, self.processdate, x) for x in adshs]
            self.dbmanager.updated_ziped_entries(update_data)
        except Exception as e:
            logging.warning(f"failed to process {filing_date}", e)

    def process(self):
        pool = Pool(8)


        entries_ready = self._read_ready_entries()
        adsh_to_process = entries_ready.accessionNumber.tolist()
        entries_sub = self._read_feed_entries_for_adshs(adsh_to_process).copy()
        grouped = entries_ready.groupby('filingDate')

        logging.info("found {} reports in {} dates to process".format(len(adsh_to_process), len(grouped)))

        param_list: List[Tuple[str, pd.DataFrame, pd.DataFrame]] = [(*entry, entries_sub) for entry in grouped]
        pool.map(self._process_date, param_list)


if __name__ == '__main__':
    dbm = DBManager("d:/secprocessing")
    creator = DailyZipCreator(dbm, "d:/tmp/daily/")
    creator.process()
