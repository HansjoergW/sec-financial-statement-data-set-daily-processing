from typing import List, Optional, Tuple

import numpy as np
import pandas as pd

from secdaily._02_xml.parsing.SecXmlParsingBase import ErrorEntry


class SECPreNumFormatter:

    def _round_half_up(self, n, decimals=0):
        # from https://realpython.com/python-rounding/#rounding-pandas-series-and-dataframe
        multiplier = 10**decimals
        return np.floor(n * multiplier + 0.5) / multiplier

    def _format_pre(self, pre_df: pd.DataFrame, adsh: Optional[str] = None) -> pd.DataFrame:
        if len(pre_df) == 0:
            return pre_df
        df = pre_df[~pre_df.stmt.isnull()]

        df = df[df.line != 0].copy()
        df["adsh"] = adsh
        df["negating"] = df.negating.astype(int)

        df.loc[df.version == "company", "version"] = adsh

        # we discovered, that comprehensive income statements are labelled as IS, if no IS is present.
        # attention: inpth has o be considered
        contained_statements = df[df.inpth == 0].stmt.unique()
        if ("CI" in contained_statements) and ("IS" not in contained_statements):
            df.loc[(df.stmt == "CI") & (df.inpth == 0), "stmt"] = "IS"

            contained_statements_inpth = df[df.inpth == 1].stmt.unique()
            if ("CI" in contained_statements_inpth) and ("IS" not in contained_statements_inpth):
                df.loc[(df.stmt == "CI") & (df.inpth == 1), "stmt"] = "IS"

        df.set_index(["adsh", "tag", "version", "report", "line", "stmt"], inplace=True)
        return df

    def _format_num(self, num_df: pd.DataFrame, adsh: Optional[str] = None) -> pd.DataFrame:
        if num_df.shape[0] == 0:
            return num_df

        num_df = num_df[
            ~num_df.tag.isin(
                [
                    "EntityCommonStockSharesOutstanding",
                    "TradingSymbol",
                    "SecurityExchangeName",
                    "CurrentFiscalYearEndDate",
                ]
            )
        ]
        df = (num_df[num_df.isrelevant]).copy()

        df["qtrs"] = df.qtrs.apply(int)
        df.loc[~df.decimals.isnull(), "value"] = pd.to_numeric(df.loc[~df.decimals.isnull(), "value"], errors="coerce")

        # sec rounds the values to 4 decimals
        # sec is not using the scientific rounding method, which rounds 0.155 up to 0.16 and 0.165 down to 0.16
        # (see https://realpython.com/python-rounding/#rounding-pandas-series-and-dataframe)

        # die 'values' in den txt files haben maximal 4 nachkommastellen...
        df.loc[~df.decimals.isnull(), "value"] = self._round_half_up(df.loc[~df.decimals.isnull(), "value"], decimals=4)

        df.loc[df.version == "company", "version"] = adsh

        df.drop(["isrelevant"], axis=1, inplace=True)
        df.drop_duplicates(inplace=True)

        # Cast 'ddate' column to int64
        df["ddate"] = df["ddate"].astype("int64")
        df["value"] = df["value"].astype("float64")
        df.loc[df.segments.isnull(), "segments"] = ""

        # set the indexes
        df.set_index(["adsh", "tag", "version", "ddate", "qtrs", "coreg", "uom"], inplace=True)

        # and sort by the precision
        # it can happen that the same tag is represented in the reports multiple times with different precision
        # and it looks as if the "txt" data of the sec is then produced with the lower precision
        df.sort_values("decimals", inplace=True)
        df_double_index_mask = df.index.duplicated(keep="first")
        df = df[~df_double_index_mask]

        df.drop(["decimals"], axis=1, inplace=True)

        return df

    def _join_pre_with_lab(self, pre_df: pd.DataFrame, lab_df: pd.DataFrame) -> pd.DataFrame:

        # Remove apostrophe from the 'label' column in lab_df
        lab_df["label"] = lab_df["label"].str.replace("’", "")

        # Set 'plabel' to 'label' if it's not set or empty
        pre_df.loc[pre_df["plabel"].isnull() | (pre_df["plabel"] == ""), "plabel"] = "label"

        pre_df["key"] = pre_df["tag"] + "#" + pre_df["version"] + "#" + pre_df["plabel"]
        pre_merged_df = pd.merge(pre_df, lab_df[["key", "label"]], on="key", how="left", suffixes=("", "_y"))
        pre_merged_df.drop(["key", "plabel"], axis=1, inplace=True)

        pre_merged_df.rename(columns={"label": "plabel"}, inplace=True)

        return pre_merged_df

    def format(
        self, adsh: str, pre_df: pd.DataFrame, num_df: pd.DataFrame, lab_df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame, List[ErrorEntry]]:
        """formats the pre and num dataframes for the provided adsh"""

        collected_errors: List[Tuple[str, str, str]] = []  # not used yet

        pre_joined = self._join_pre_with_lab(pre_df, lab_df)

        pre_formatted_df = self._format_pre(pre_joined, adsh).reset_index()
        num_formatted_df = self._format_num(num_df, adsh).reset_index()

        # only keep entries that have keys on both side
        key_columns = ["adsh", "tag", "version"]
        merged_df = pd.merge(pre_formatted_df[key_columns], num_formatted_df[key_columns], on=key_columns, how="inner")

        pre_merged_df = pre_formatted_df[
            pre_formatted_df[key_columns].apply(tuple, axis=1).isin(merged_df[key_columns].apply(tuple, axis=1))
        ]
        num_merged_df = num_formatted_df[
            num_formatted_df[key_columns].apply(tuple, axis=1).isin(merged_df[key_columns].apply(tuple, axis=1))
        ]

        sec_error_list = [ErrorEntry(adsh=x[0], error_info=x[1], error=x[2]) for x in collected_errors]

        return (pre_merged_df, num_merged_df, sec_error_list)
