from _02_xml.SecXmlParsingBase import SecXmlParserBase, SecError
from _02_xml.num._1_SecNumXmlExtracting import SecNumXmlExtractor, SecNumExtraction
from _02_xml.num._2_SecNumXmlTransformation import SecNumXmlTransformer, SecNumTransformed, SecNumTransformedContext, SecNumTransformedTag

import pandas as pd

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

            temp_dict = {}
            temp_dict['adsh'] = adsh
            temp_dict['tag'] = tag.tagname
            temp_dict['version'] = tag.version
            temp_dict['uom'] = tag.unitref
            temp_dict['value'] = tag.valuetxt
            temp_dict['decimals'] = tag.decimals
            temp_dict['ddate'] = context_entry.enddate
            temp_dict['qtrs'] = context_entry.qtrs
            temp_dict['segments'] = context_entry.segments
            temp_dict['coreg'] = ''
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

    def clean_for_financial_statement_dataset(self, df: pd.DataFrame, adsh: str = None) -> pd.DataFrame:
        if df.shape[0] == 0:
            return df

        df = (df[df.segments.isnull()]).copy()

        df['qtrs'] = df.qtrs.apply(int)
        df['value'] = pd.to_numeric(df['value'], errors='coerce')

        # die 'values' in den txt files haben maximal 4 nachkommastellen...
        df['value'] = df.value.round(4)

        df.loc[df.version == 'company', 'version'] = adsh

        df.drop(['segments'], axis=1, inplace=True)
        df.drop_duplicates(inplace=True)

        # set the indexes
        df.set_index(['adsh', 'tag', 'version', 'ddate', 'qtrs'], inplace=True)

        # and sort by the precision
        # it can happen that the same tag is represented in the reports multiple times with different precision
        # and it looks as if the "txt" data of the sec is then produced with the lower precision
        df.sort_values('decimals', inplace=True)
        df_double_index_mask = df.index.duplicated(keep='first')

        df = df[~df_double_index_mask]

        return df
