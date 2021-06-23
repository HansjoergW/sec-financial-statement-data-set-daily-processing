from _00_common.DBManagement import DBManager
from _00_common.SecFileUtils import read_df_from_zip
from typing import List

import pandas as pd

class DailyZipCreator:

    def __init__(self, dbmanager: DBManager):
        self.dbmanager = dbmanager

    def _read_ready_entries(self) -> pd.DataFrame:
        return self.dbmanager.find_ready_to_zip_adshs()

    def _read_csvfiles(self, filelist: List[str]) -> str:
        dfs = [read_df_from_zip(file) for file in filelist]
        return pd.concat(dfs).to_csv(sep="\t", header=True, index=False)

    def _create_sub_file(self, adshs: List[str]) -> str:
        # todo
        return ""

    def _create_daily_zip(self, date:str, entries: pd.DataFrame):
        #verzeichnis anlegen? oder ist es nur der Filename?
        # -> content = pandas.to_csv()
        #prefiles zu einem einzigen Datensatz zusammenfassen
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