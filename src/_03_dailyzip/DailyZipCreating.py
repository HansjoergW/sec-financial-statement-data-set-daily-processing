from _00_common.DBManagement import DBManager
from _00_common.SecFileUtils import read_df_from_zip
from typing import List

import pandas as pd
import numpy as np

class DailyZipCreator:

    def __init__(self, dbmanager: DBManager):
        self.dbmanager = dbmanager
        self.copied_df = dbmanager.read_all_copied()

    def _read_ready_entries(self) -> pd.DataFrame:
        return self.dbmanager.find_ready_to_zip_adshs()

    def _read_feed_entries_for_adshs(self, adshs: List[str]) -> pd.DataFrame:
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

        feed_entries = self.dbmanager.read_all_copied()
        feed_entries = feed_entries[feed_entries.accessionNumber.isin(adshs)]

        sub_entries = feed_entries[['accessionNumber','cikNumber', 'companyName','assignedSic','fiscalYearEnd','formType','period','filingDate','acceptanceDatetime']].copy()

        # rename to sub-file column names
        sub_entries.rename(columns = {'accessionNumber': 'adsh',
                                      'cikNumber': 'cik',
                                      'companyName': 'name',
                                      'assignedSic': 'sic',
                                      'fiscalYearEnd': 'fye',
                                      'formType': 'form',
                                      'filingDate': 'filed',
                                      'acceptanceDatetime': 'accepted'}, inplace=True)

        # convertions
        sub_entries['cik'] = sub_entries.cik.astype(int)
        sub_entries['name'] = sub_entries.name.str.upper()

        # check for Null Values in fye
        # there are some entries, which don't have a fye entry. if it is a 10-k, then this is the month and year of period
        sub_entries.loc[sub_entries.fye.isnull() & (sub_entries.form == '10-K'), 'fye'] = sub_entries.period.str.slice(4,8)
        # if it is a 10-q, we cannot say...
        sub_entries.loc[sub_entries.fye.isnull(), 'fye'] = "0000"

        # create helper columns
        sub_entries['period_year'] = sub_entries.period.str.slice(0,4).astype(int)
        sub_entries['period_month'] = sub_entries.period.str.slice(4,6).astype(int)
        sub_entries['period_day'] = sub_entries.period.str.slice(6,8).astype(int)

        sub_entries['fye_month'] = sub_entries.fye.str.slice(0,2).astype(int)
        sub_entries['fye_day'] = sub_entries.fye.str.slice(2,4).astype(int)
        # correction for 29 of feb in order to not run into problems later on
        sub_entries.loc[(sub_entries.fye_month==2) & (sub_entries.fye_day==29), 'fye_day'] = 28

        sub_entries['is_fye_same_year'] = (sub_entries.form == '10-K') | ((sub_entries.fye_month*100+sub_entries.fye_day) >= (sub_entries.period_month*100+sub_entries.period_day))

        # fy
        sub_entries.loc[sub_entries.is_fye_same_year,'fy'] = sub_entries.period_year
        sub_entries.loc[sub_entries.is_fye_same_year == False,'fy'] = sub_entries.period_year + 1
        sub_entries.fy = sub_entries.fy.astype(int)

        sub_entries.loc[sub_entries.fye == '0000','fy'] = 0 # cannot be calculated, if there was no fye entry

        # fp
        sub_entries['period_date'] = pd.to_datetime(sub_entries.period, format='%Y%m%d')
        sub_entries['fye_date'] = pd.to_datetime(sub_entries.fy*10000+sub_entries.fye_month*100+sub_entries.fye_day,format='%Y%m%d', errors='coerce')

        sub_entries['fye_period_diff'] = 0

        sub_entries.loc[sub_entries.fye != '0000', 'fye_period_diff'] = (sub_entries.fye_date - sub_entries.period_date) / np.timedelta64(1,'D')

        sub_entries.loc[sub_entries.form == '10-K','fp'] = 'FY'
        sub_entries.loc[sub_entries.form != '10-K' ,'fp'] = 'Q' + (sub_entries.fye_period_diff / 91.5).round().astype(str).str.slice(0,1)
        sub_entries.loc[sub_entries.fye == '0000','fp'] = 'Q0' # cannot be calculated, if there was no fye entry
        

        #  07/01/2021-> 20210107
        sub_entries['filed'] = pd.to_datetime(sub_entries.filed, format='%m/%d/%Y')
        sub_entries['filed'] = sub_entries.filed.dt.strftime('%Y%m%d')

        # accepted -> 20210107161557 rounded to minutes
        # 20210107132023-> 07.01.2021 13:20:00.0
        sub_entries['accepted'] = pd.to_datetime(sub_entries.accepted, format='%Y%m%d%H%M%S')
        sub_entries['accepted'] = sub_entries.accepted.dt.strftime('%d.%m.%Y %H:%M:00.0')

        # drop helper columns
        sub_entries.drop(columns=['period_year', 'period_month', 'period_day', 'fye_month',
                                  'fye_day', 'is_fye_same_year', 'fye_date', 'period_date', 'fye_period_diff'], inplace=True)

        return sub_entries

    def _read_csvfiles(self, filelist: List[str]) -> str:
        dfs = [read_df_from_zip(file) for file in filelist]
        return pd.concat(dfs).to_csv(sep="\t", header=True, index=False)

    def _create_daily_zip(self, date:str, entries: pd.DataFrame, entries_sub_df: pd.DataFrame):
        sub_content = entries_sub_df.to_csv(sep="\t", header=True, index=False)
        pre_content = self._read_csvfiles(entries.csvPreFile.tolist())
        num_content = self._read_csvfiles(entries.csvNumFile.tolist())
        print("")

        # alle files zippen
        pass

    def _iterate_filing_dates(self):
        entries_ready = self._read_ready_entries()
        entries_sub = self._read_feed_entries_for_adshs(entries_ready.accessionNumber.tolist()).copy()

        grouped = entries_ready.groupby('filingDate')
        for entry, df in grouped:
            adshs = df.accessionNumber.tolist()
            self._create_daily_zip(entry, df, entries_sub[entries_sub.adsh.isin(adshs)])
            print(entry, len(df), df.columns)
            # update db eintrag für alle Files



if __name__ == '__main__':
    dbm = DBManager("d:/secprocessing")
    creator = DailyZipCreator(dbm)
    creator._iterate_filing_dates()

    print()


""" 
adsh	cik	name	sic	fye	form	period	fy	fp	filed	accepted
0001493152-21-000456	715446	ANIXA BIOSCIENCES INC		1031	10-K	20201031	2020	FY	20210107	07.01.2021 16:16
0001437749-21-000341	76267	PARK AEROSPACE CORP		229	10-Q	20201130	2021	Q3	20210107	07.01.2021 13:20
0001564590-21-000486	1687221	REV GROUP, INC.		1031	10-K	20201031	2020	FY	20210107	07.01.2021 07:11

edgar:accessionNumber	
edgar:cikNumber	/ no leading zeros
edgar:companyName	/ upper case
edgar:assignedSic
edgar:fiscalYearEnd	 / MMDD /  "with leading zero / 0228 ->rounded to 0229 in leap year
edgar:formType
edgar:period			edgar:fillingDate	edgar:acceptanceDatetime

fy: / "actual year for 10K /year for next 10K"	
fp: / "FY for 10K / actual Quarter"

edgar:fillingDate01.07.2021
edgar:acceptanceDatetime /	"like: 20210107161557 / rounded to minutes"

"""