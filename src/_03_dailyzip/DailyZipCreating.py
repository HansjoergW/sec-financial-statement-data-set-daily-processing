from _00_common.DBManagement import DBManager
from _00_common.SecFileUtils import read_df_from_zip
from typing import List

import pandas as pd

class DailyZipCreator:

    def __init__(self, dbmanager: DBManager):
        self.dbmanager = dbmanager
        self.copied_df = dbmanager.read_all_copied()

    def _read_ready_entries(self) -> pd.DataFrame:
        return self.dbmanager.find_ready_to_zip_adshs()

    def _read_csvfiles(self, filelist: List[str]) -> str:
        dfs = [read_df_from_zip(file) for file in filelist]
        return pd.concat(dfs).to_csv(sep="\t", header=True, index=False)

    def _calc_fiscal_date_cols(self, row_series):
        is_10k = True if row_series.form=='10-K' else False

        # calculate end of last fiscal year
        period_year =


        # fp -> Q1, Q2, Q3, FY
        #    -> tage berechnen
        #       -> wenn fye für periode jahr bereits vorbei -> distanz seit fye diesem jahr
        #       -> sonst distand seit fye letztem jahr ->
        # fy -> ende des fiscal years
        #  -> vergleich mit periode und mit fye
        #  -> wenn fye für periode jahr bereits vorbei -> next year, sonst period year


        row_series['fp'] = '_'
        row_series['fy'] = '_'
        return row_series

    def _create_sub_content(self, adshs: List[str]) -> str:

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


        sub_entries = self.copied_df[self.copied_df.accessionNumber.isin(adshs)].copy()
        sub_entries = sub_entries[['accessionNumber','cikNumber', 'companyName','assignedSic','fiscalYearEnd','formType','period','filingDate','acceptanceDatetime']]

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

        period_year, month, day berechnen

        sub_entries = sub_entries.apply(self._calc_fiscal_date_cols, axis=1)

        #  07/01/2021-> 20210107
        sub_entries['filed'] = pd.to_datetime(sub_entries.filed, format='%d/%m/%Y')
        sub_entries['filed'] = sub_entries.filed.dt.strftime('%Y%m%d')

        # accepted -> 20210107161557 rounded to minutes
        # 20210107132023-> 07.01.2021 13:20:00.0
        sub_entries['accepted'] = pd.to_datetime(sub_entries.accepted, format='%Y%m%d%H%M%S')
        sub_entries['accepted'] = sub_entries.accepted.dt.strftime('%d.%m.%Y %H:%M:00.0')

        period_cols wieder entfernen

        return sub_entries.to_csv(sep="\t", header=True, index=False)




    def _create_daily_zip(self, date:str, entries: pd.DataFrame):
        #verzeichnis anlegen? oder ist es nur der Filename?
        # -> content = pandas.to_csv()
        #prefiles zu einem einzigen Datensatz zusammenfassen
        sub_content = self._create_sub_content(entries.accessionNumber.tolist())
        pre_content = self._read_csvfiles(entries.csvPreFile.tolist())
        num_content = self._read_csvfiles(entries.csvNumFile.tolist())
        print("")

        #subfile erzeugen
        # alle files zippen

        pass

    def _iterate_filing_dates(self):
        entries = self._read_ready_entries()
        grouped = entries.groupby('filingDate')
        for entry, df in grouped:
            print(entry, len(df), df.columns)
            self._create_daily_zip(entry, df)
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