from _02_xml.parsing.SecXmlParsingBase import SecXmlParserBase, SecError
from _02_xml.parsing.num._1_SecNumXmlExtracting import SecNumXmlExtractor, SecNumExtraction
from _02_xml.parsing.num._2_SecNumXmlTransformation import SecNumXmlTransformer, SecNumTransformed, SecNumTransformedContext, SecNumTransformedTag, SecNumTransformedUnit

import pandas as pd
import numpy as np

from typing import Dict, List, Tuple, Optional


class SecNumXmlParser(SecXmlParserBase):
    """ Parses the data of an Num.Xml file and delivers the data in a similar format than the num.txt
       contained in the financial statements dataset of the sec."""

    def __init__(self):
        super(SecNumXmlParser, self).__init__("num")
        pass

    def _read_tags(self, adsh:str, transformed_data: SecNumTransformed) -> pd.DataFrame:

        entries = []
        tag:SecNumTransformedTag
        for tag in transformed_data.tag_list:

            context_entry:SecNumTransformedContext = transformed_data.contexts_map[tag.ctxtref]

            uom = None
            if tag.unitref is not None:
                unit_entry:SecNumTransformedUnit = transformed_data.units_map[tag.unitref]

                uom = unit_entry.uom
                # uom entries have a max length of 20
                uom = uom[:min(len(uom), 20)]

            decimals = tag.decimals
            if decimals:
                # decimal string contains often a -, but this leads to a wrong order if we want to compare as string
                decimals = decimals.replace("-","")

                # sometimes INF is used instead of 0, which also indicates an  unrounded number
                if decimals == 'INF':
                    decimals = '0'

            temp_dict = {}
            temp_dict['adsh'] = adsh
            temp_dict['tag'] = tag.tagname
            temp_dict['version'] = tag.version
            temp_dict['uom'] = uom
            temp_dict['value'] = tag.valuetxt
            temp_dict['decimals'] = decimals
            temp_dict['ddate'] = context_entry.enddate
            temp_dict['qtrs'] = context_entry.qtrs
            temp_dict['segments'] = context_entry.segments
            temp_dict['coreg'] = context_entry.coreg
            temp_dict['isrelevant'] = context_entry.isrelevant
            temp_dict['footnote'] = ''

            entries.append(temp_dict)

        return pd.DataFrame(entries)

    def parse(self, adsh: str, data: str) -> Tuple[pd.DataFrame, List[SecError]]:
        extractor: SecNumXmlExtractor = SecNumXmlExtractor()
        transformer: SecNumXmlTransformer = SecNumXmlTransformer()

        extracted_data: SecNumExtraction = extractor.extract(adsh, data)
        transformed_data: SecNumTransformed = transformer.transform(adsh, extracted_data)

        df = self._read_tags(adsh, transformed_data)
        return df, []

    def round_half_up(self, n, decimals=0):
        # from https://realpython.com/python-rounding/#rounding-pandas-series-and-dataframe
        multiplier = 10 ** decimals
        return np.floor(n*multiplier + 0.5) / multiplier

    def clean_for_financial_statement_dataset(self, df: pd.DataFrame, adsh: str = None) -> pd.DataFrame:
        if df.shape[0] == 0:
            return df

        df = (df[df.isrelevant]).copy()

        df['uom_ext'] = df['uom']

        # in order to be able to distinguish stock classes, uom has to be extended with the appropriate dimension
        df.loc[df.tag == 'EntityCommonStockSharesOutstanding', 'uom_ext'] = df[df.tag == 'EntityCommonStockSharesOutstanding'].uom + "_" + df[df.tag == 'EntityCommonStockSharesOutstanding'].segments.apply(lambda x: x[0].label)
        df.loc[df.tag == 'TradingSymbol', 'uom_ext'] = df[df.tag == 'TradingSymbol'].segments.apply(lambda x: x[0].label)
        df.loc[df.tag == 'SecurityExchangeName', 'uom_ext'] = df[df.tag == 'SecurityExchangeName'].segments.apply(lambda x: x[0].label)

        df['qtrs'] = df.qtrs.apply(int)
        df.loc[~df.decimals.isnull(), 'value'] = pd.to_numeric(df.loc[~df.decimals.isnull(), 'value'], errors='coerce')

        # sec rounds the values to 4 decimals
        # sec is not using the scientific rounding method, which rounds 0.155 up to 0.16 and 0.165 down to 0.16
        # (see https://realpython.com/python-rounding/#rounding-pandas-series-and-dataframe)

        # die 'values' in den txt files haben maximal 4 nachkommastellen...
        df.loc[~df.decimals.isnull(), 'value'] = self.round_half_up( df.loc[~df.decimals.isnull(), 'value'], decimals=4)

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

        return df
