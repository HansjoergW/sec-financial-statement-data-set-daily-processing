import logging
import os
import zipfile
from multiprocessing import Pool
from typing import Dict, List, Protocol, Tuple

import numpy as np
import pandas as pd

from secdaily._00_common.BaseDefinitions import DTYPES_NUM, DTYPES_PRE, MONTH_TO_QRTR
from secdaily._00_common.ProcessBase import ProcessBase
from secdaily._00_common.SecFileUtils import read_df_from_zip
from secdaily._04_dailyzip.db.DailyZipCreatingDataAccess import DailyZipCreatingDA, UpdateDailyZip


class DataAccess(Protocol):

    def read_all_copied(self) -> pd.DataFrame:
        """read all entries from the feed table"""
        return pd.DataFrame()

    def find_ready_to_zip_adshs(self) -> pd.DataFrame:
        """find all entries that are ready to be packed into a daily zip file"""
        return pd.DataFrame()

    def updated_ziped_entries(self, update_list: List[UpdateDailyZip]):
        """update the daily zip file information for the given entries"""


class DailyZipCreator(ProcessBase):
    """
    This class will find all the filing dates for which there are entries in the processing table that to have
    processed num and pre file, but haven't packed into a daily zip file.
    It will then select all the entries that have one of the found filing dates, regardless, if the entry
    already was packed into a dailyzip file for his filing date.
    That means, that a dailyzip could be recreated, if a previously failed to process entry can now be recreated.
    So it is important to keep track of the day/time when the dailyzip file was created, since its content could
    change.
    """

    def __init__(self, dbmanager: DataAccess, data_dir: str = "./tmp/daily/"):
        super().__init__(data_dir=data_dir)

        self.dbmanager = dbmanager

    def _read_feed_entries_for_adshs(self, adshsAndFye: pd.DataFrame) -> pd.DataFrame:
        feed_entries = self.dbmanager.read_all_copied()
        adshs = adshsAndFye.accessionNumber.tolist()
        feed_entries = feed_entries[feed_entries.accessionNumber.isin(adshs)]

        adshsAndFye["fiscalYearEnd"] = adshsAndFye.fiscalYearEnd.str.strip()
        adshsAndFye.set_index("accessionNumber", inplace=True)
        fye_dict: Dict[str, str] = adshsAndFye.to_dict()["fiscalYearEnd"]

        return self._create_sub_df(feed_entries, fye_dict)

    def _read_ready_entries(self) -> pd.DataFrame:
        return self.dbmanager.find_ready_to_zip_adshs()

    def _create_sub_df(self, df: pd.DataFrame, fye_dict: Dict[str, str]) -> pd.DataFrame:
        # fye contains the fiscalYearEnd information that were read from the num-xml file
        #
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

        sub_entries = df[
            [
                "accessionNumber",
                "cikNumber",
                "companyName",
                "assignedSic",
                "fiscalYearEnd",
                "formType",
                "period",
                "filingDate",
                "acceptanceDatetime",
            ]
        ].copy()

        # we prefer the fye information from the num file, so first we add the information from the fye_dict
        # as a new column
        sub_entries["numFye"] = sub_entries.accessionNumber.map(fye_dict)
        # the we replace the existing fiscalYearEnd info with the numFye column, if the numFye contains data
        sub_entries.loc[~sub_entries.numFye.isnull(), "fiscalYearEnd"] = sub_entries["numFye"]
        sub_entries.drop(columns=["numFye"], inplace=True)

        # rename to sub-file column names
        sub_entries.rename(
            columns={
                "accessionNumber": "adsh",
                "cikNumber": "cik",
                "companyName": "name",
                "assignedSic": "sic",
                "fiscalYearEnd": "fye",
                "formType": "form",
                "filingDate": "filed",
                "acceptanceDatetime": "accepted",
            },
            inplace=True,
        )

        if len(sub_entries) == 0:
            return sub_entries

        # simple conversions
        sub_entries["cik"] = sub_entries.cik.astype(int)
        sub_entries["name"] = sub_entries.name.str.upper()
        sub_entries["name"] = sub_entries.name.str.replace("\\", "", regex=False)

        # check for Null Values in fye
        # there are some entries, which don't have a fye entry.
        # if it is a 10-k, then this is the month and year of period
        sub_entries.loc[sub_entries.fye.isnull() & (sub_entries.form == "10-K"), "fye"] = sub_entries.period.str.slice(
            4, 8
        )
        # if it is a 10-q, we cannot say...
        sub_entries.loc[sub_entries.fye.isnull(), "fye"] = "0000"

        # create helper columns
        sub_entries["period_date"] = pd.to_datetime(sub_entries.period, format="%Y%m%d")
        sub_entries["period_year"] = sub_entries.period.str.slice(0, 4).astype(int)
        sub_entries["period_month"] = sub_entries.period.str.slice(4, 6).astype(int)
        sub_entries["period_day"] = sub_entries.period.str.slice(6, 8).astype(int)

        # round period to end of month
        mask = (sub_entries.period_day <= 15) | (
            (sub_entries.period_day == 16) & sub_entries.period_month.isin([1, 3, 5, 7, 8, 10, 12])
        )
        sub_entries.loc[mask, "period_date"] = sub_entries.period_date - pd.DateOffset(months=1)  # type: ignore
        sub_entries["period"] = (
            sub_entries.period_date.dt.to_period("M").dt.to_timestamp("M").dt.strftime("%Y%m%d")
        )  # type: ignore
        # Nach Korrektur neu setzen
        sub_entries["period_date"] = pd.to_datetime(sub_entries.period, format="%Y%m%d")

        # after calculation of the period, the values might have changed
        sub_entries["period_year"] = sub_entries.period.str.slice(0, 4).astype(int)
        sub_entries["period_month"] = sub_entries.period.str.slice(4, 6).astype(int)
        sub_entries["period_day"] = sub_entries.period.str.slice(6, 8).astype(int)

        sub_entries["fye_month"] = sub_entries.fye.str.slice(0, 2).astype(int)
        sub_entries["fye_day"] = sub_entries.fye.str.slice(2, 4).astype(int)

        # attention: month and day may be 0
        # so finding the closest month end for fye
        mask = ((sub_entries.fye_day <= 15) & (sub_entries.fye_day > 0)) | (
            (sub_entries.fye_day == 16) & sub_entries.fye_month.isin([1, 3, 5, 7, 8, 10, 12])
        )
        sub_entries.loc[mask, "fye_month"] = sub_entries.fye_month - 1
        # if fye_month has been 1 in the line above, it becomes 0, so we have to correct that to 12
        mask = (sub_entries.fye_day > 0) & (sub_entries.fye_month == 0)
        sub_entries.loc[mask, "fye_month"] = 12

        month_end = {0: 0, 1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
        sub_entries["fye_day"] = sub_entries.fye_month.map(month_end)
        sub_entries["fye"] = sub_entries.fye_month * 100 + sub_entries.fye_day
        sub_entries["fye"] = sub_entries.fye.astype(str).str.zfill(4)

        # correction for 29 of feb in order to not run into problems later on
        sub_entries.loc[(sub_entries.fye_month == 2) & (sub_entries.fye_day == 29), "fye_day"] = 28

        sub_entries["is_fye_same_year"] = (sub_entries.form == "10-K") | (
            (sub_entries.fye_month * 100 + sub_entries.fye_day)
            >= (sub_entries.period_month * 100 + sub_entries.period_day)
        )

        # fy_real -> year when the next fiscal year ends
        sub_entries.loc[sub_entries.is_fye_same_year, "fy_real"] = sub_entries.period_year
        sub_entries.loc[sub_entries.is_fye_same_year == False, "fy_real"] = (  # noqa: E712 pylint: disable=C0121
            sub_entries.period_year + 1
        )

        sub_entries.fy_real = sub_entries.fy_real.astype(int)

        # fy -> as it seems is the previous year, if the year ends in the first quarter,
        # at least that is always true for 10-K
        sub_entries["fy"] = sub_entries.fy_real
        # if a 10-K ends in the first three months, then its fy is the one from last year
        mask_10k_firstq = (sub_entries.form == "10-K") & (sub_entries.fye_month.isin([1, 2, 3]))
        mask_10k_firstq = sub_entries.fye_month.isin([1, 2, 3])
        sub_entries.loc[mask_10k_firstq, "fy"] = sub_entries.fy - 1

        sub_entries.loc[sub_entries.fye == "0000", "fy"] = 0  # cannot be calculated, if there was no fye entry

        # fp
        #  date when the last fiscal year ended
        sub_entries["fye_date_prev"] = pd.to_datetime(
            (sub_entries.fy_real - 1) * 10000 + sub_entries.fye_month * 100 + sub_entries.fye_day,
            format="%Y%m%d",
            errors="coerce",
        )

        sub_entries["fye_period_diff"] = 0

        sub_entries.loc[sub_entries.fye != "0000", "fye_period_diff"] = (
            sub_entries.period_date - sub_entries.fye_date_prev
        ) / np.timedelta64(
            1, "D"
        )  # type: ignore

        sub_entries.loc[sub_entries.form == "10-K", "fp"] = "FY"
        sub_entries.loc[sub_entries.form != "10-K", "fp"] = "Q" + (sub_entries.fye_period_diff / 91.5).round().astype(
            str
        ).str.slice(0, 1)
        sub_entries.loc[sub_entries.fye == "0000", "fp"] = "Q0"  # cannot be calculated, if there was no fye entry

        #  07/01/2021-> 20210107
        sub_entries["filed"] = pd.to_datetime(sub_entries.filed, format="%m/%d/%Y")
        sub_entries["filed"] = sub_entries.filed.dt.strftime("%Y%m%d")

        # accepted -> 20210107161557 rounded to minutes
        # 20210107132023-> 07.01.2021 13:20:00.0
        sub_entries["accepted"] = pd.to_datetime(sub_entries.accepted, format="%Y%m%d%H%M%S")
        sub_entries["accepted"] = sub_entries.accepted.dt.round("min")
        sub_entries["accepted"] = sub_entries.accepted.dt.strftime("%Y-%m-%d %H:%M:00.0")

        # drop helper columns
        sub_entries.drop(
            columns=[
                "period_year",
                "period_month",
                "period_day",
                "fye_month",
                "fye_day",
                "is_fye_same_year",
                "fye_date_prev",
                "period_date",
                "fye_period_diff",
            ],
            inplace=True,
        )

        return sub_entries

    def _read_csvfiles(self, filelist: List[str], dtype) -> str:
        dfs = [read_df_from_zip(filename=file, dtype=dtype) for file in filelist]
        # Filter out empty DataFrames to avoid FutureWarning
        non_empty_dfs = [df for df in dfs if not df.empty]
        if not non_empty_dfs:
            # If all DataFrames are empty, create an empty DataFrame with the expected columns
            # based on the dtype parameter
            logging.warning("All DataFrames are empty: %s ... ", str(filelist)[0:50])
            empty_df = pd.DataFrame(columns=list(dtype.keys()))
            return empty_df.to_csv(sep="\t", header=True, index=False)
        return pd.concat(non_empty_dfs).to_csv(sep="\t", header=True, index=False)

    def _get_qrtr(self, filing_date: str) -> str:
        year = filing_date[6:]
        month = filing_date[0:2]
        month_int = int(month)
        qtr = MONTH_TO_QRTR[month_int]

        return year + "q" + str(qtr)

    def _store_to_zip(self, filing_date: str, sub: str, pre: str, num: str) -> str:
        qrtr = self._get_qrtr(filing_date)
        qtr_dir = os.path.join(self.data_dir, qrtr)
        os.makedirs(os.path.join(qtr_dir), exist_ok=True)

        year = filing_date[6:]
        month = filing_date[0:2]
        day = filing_date[3:5]
        zipfile_name = year + month + day + ".zip"
        zipfile_path = os.path.join(qtr_dir, zipfile_name)
        with zipfile.ZipFile(zipfile_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("sub.txt", sub)
            zf.writestr("pre.txt", pre)
            zf.writestr("num.txt", num)

        return zipfile_path

    def _create_daily_content(self, entries_df: pd.DataFrame, entries_sub_df: pd.DataFrame) -> Tuple[str, str, str]:
        sub_content = entries_sub_df.to_csv(sep="\t", header=True, index=False)
        pre_content = self._read_csvfiles(entries_df.preFormattedFile.tolist(), DTYPES_PRE)
        num_content = self._read_csvfiles(entries_df.numFormattedFile.tolist(), DTYPES_NUM)
        return sub_content, pre_content, num_content

    def _process_date(self, data: Tuple[str, pd.DataFrame, pd.DataFrame]):
        filing_date: str = data[0]
        group_df: pd.DataFrame = data[1]
        entries_sub: pd.DataFrame = data[2]

        try:
            adshs = group_df.accessionNumber.tolist()
            sub, pre, num = self._create_daily_content(
                entries_df=group_df, entries_sub_df=entries_sub[entries_sub.adsh.isin(adshs)]
            )
            zipfile_path = self._store_to_zip(filing_date, sub, pre, num)
            update_data = [
                UpdateDailyZip(accessionNumber=x, dailyZipFile=zipfile_path, processZipDate=self.processdate)
                for x in adshs
            ]
            self.dbmanager.updated_ziped_entries(update_data)
        except Exception as e:  # pylint: disable=broad-except
            logging.warning("failed to process %s / %s", filing_date, e)

    def process(self):
        logging.info("Daily zip creating")

        with Pool(8) as pool:
            entries_ready = self._read_ready_entries()
            adsh_and_fye_to_process = entries_ready[["accessionNumber", "fiscalYearEnd"]].copy()
            entries_sub = self._read_feed_entries_for_adshs(adsh_and_fye_to_process).copy()
            grouped = entries_ready.groupby("filingDate")

            logging.info("found %d reports in %d dates to process", len(adsh_and_fye_to_process), len(grouped))

            # entry[0] is the date
            # entry[1] is the group as dataframe
            param_list: List[Tuple[str, pd.DataFrame, pd.DataFrame]] = [
                (str(entry[0]), entry[1], entries_sub) for entry in grouped
            ]
            pool.map(self._process_date, param_list)


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d:%H:%M:%S",
        level=logging.DEBUG,
    )

    dbm = DailyZipCreatingDA("d:/secprocessing2")
    creator = DailyZipCreator(dbm, "d:/tmp/daily/")
    creator.process()
