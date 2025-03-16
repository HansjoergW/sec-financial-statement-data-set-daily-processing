from typing import Optional
import numpy as np
import pandas as pd


class SECStyleFormatter:

    def __init__(self, csv_dir: str):  
        self._csv_dir = csv_dir


    def _round_half_up(self, n, decimals=0):
        # from https://realpython.com/python-rounding/#rounding-pandas-series-and-dataframe
        multiplier = 10 ** decimals
        return np.floor(n*multiplier + 0.5) / multiplier
    
    def _format_pre(self, pre_df: pd.DataFrame, adsh: Optional[str] = None) -> pd.DataFrame:
        if len(pre_df) == 0:
            return pre_df
        df = pre_df[~pre_df.stmt.isnull()]

        df = df[df.line != 0].copy()
        df['adsh'] = adsh
        df['negating'] = df.negating.astype(int)

        df.loc[df.version == 'company', 'version'] = adsh

        # we discovered, that comprehensive income statements are labelled as IS, if no IS is present.
        # attention: inpth has o be considered
        contained_statements = df[df.inpth==0].stmt.unique()
        if ("CI" in contained_statements) and ("IS" not in contained_statements):
            df.loc[(df.stmt == 'CI') & (df.inpth==0), 'stmt'] = 'IS'

            contained_statements_inpth = df[df.inpth==1].stmt.unique()
            if ("CI" in contained_statements_inpth) and ("IS" not in contained_statements_inpth):
                df.loc[(df.stmt == 'CI') & (df.inpth==1), 'stmt'] = 'IS'

        df.set_index(['adsh', 'tag', 'version', 'report', 'line', 'stmt'], inplace=True)
        return df

    def _format_num(self, num_df: pd.DataFrame, adsh: Optional[str] = None) -> pd.Tuple[pd.DataFrame, Optional[str]]:
        if num_df.shape[0] == 0:
            return num_df, None

        df = (num_df[num_df.isrelevant]).copy()

        df['uom_ext'] = df['uom']

        # in order to be able to distinguish stock classes, uom has to be extended with the appropriate dimension

        df.loc[(df.tag == 'EntityCommonStockSharesOutstanding') & (~df.segments.isnull()), 'uom_ext'] = df[(df.tag == 'EntityCommonStockSharesOutstanding') & (~df.segments.isnull())].uom + "_" + df[(df.tag == 'EntityCommonStockSharesOutstanding') & (~df.segments.isnull())].segments.apply(lambda x: x[0].label)
        df.loc[(df.tag == 'TradingSymbol') & (~df.segments.isnull()), 'uom_ext'] = df[(df.tag == 'TradingSymbol')  & (~df.segments.isnull())].segments.apply(lambda x: x[0].label)
        df.loc[(df.tag == 'SecurityExchangeName') & (~df.segments.isnull()), 'uom_ext'] = df[(df.tag == 'SecurityExchangeName')  & (~df.segments.isnull())].segments.apply(lambda x: x[0].label)

        # current fiscal year end appears in the form --MM-dd, so we remove the dashes
        df.loc[(df.tag == 'CurrentFiscalYearEndDate'), 'value'] = df[df.tag == 'CurrentFiscalYearEndDate'].value.str.replace('-','')

        # check wether a currentfiscalyearenddate is present -> we return that as a separate information
        cfyed_df = df[(df.tag == 'CurrentFiscalYearEndDate')]
        if len(cfyed_df) > 0:
            fiscalYearEnd = cfyed_df.value.iloc[0]
        else:
            fiscalYearEnd = None

        df['qtrs'] = df.qtrs.apply(int)
        df.loc[~df.decimals.isnull(), 'value'] = pd.to_numeric(df.loc[~df.decimals.isnull(), 'value'], errors='coerce')

        # sec rounds the values to 4 decimals
        # sec is not using the scientific rounding method, which rounds 0.155 up to 0.16 and 0.165 down to 0.16
        # (see https://realpython.com/python-rounding/#rounding-pandas-series-and-dataframe)

        # die 'values' in den txt files haben maximal 4 nachkommastellen...
        df.loc[~df.decimals.isnull(), 'value'] = self._round_half_up( df.loc[~df.decimals.isnull(), 'value'], decimals=4)

        df.loc[df.version == 'company', 'version'] = adsh

        df.drop(['segments','isrelevant'], axis=1, inplace=True)
        df.drop_duplicates(inplace=True)

        # set the indexes
        df.set_index(['adsh', 'tag', 'version', 'ddate', 'qtrs', 'coreg', 'uom_ext'], inplace=True)

        # and sort by the precision
        # it can happen that the same tag is represented in the reports multiple times with different precision
        # and it looks as if the "txt" data of the sec is then produced with the lower precision
        df.sort_values('decimals', inplace=True)
        df_double_index_mask = df.index.duplicated(keep='first')

        df = df[~df_double_index_mask]

        return df, fiscalYearEnd



    def process(self):
        pass
