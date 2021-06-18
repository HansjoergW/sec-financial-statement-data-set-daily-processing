from _02_xml.parsing.SecXmlParsingBase import SecXmlParserBase, SecError
from _02_xml.parsing.num._1_SecNumXmlExtracting import SecNumXmlExtractor, SecNumExtraction
from _02_xml.parsing.num._2_SecNumXmlTransformation import SecNumXmlTransformer, SecNumTransformed, SecNumTransformedContext, SecNumTransformedTag, SecNumTransformedUnit

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
            unit_entry:SecNumTransformedUnit = transformed_data.units_map[tag.unitref]

            uom = unit_entry.uom
            # uom entries have a max length of 20
            uom = uom[:min(len(uom), 20)]

            # string contains often a -, but this leads to a wrong order if we want to compare as string
            decimals = tag.decimals
            if decimals:
                decimals = decimals.replace("-","")

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

    def clean_for_financial_statement_dataset(self, df: pd.DataFrame, adsh: str = None) -> pd.DataFrame:
        if df.shape[0] == 0:
            return df

        df = (df[df.isrelevant]).copy()

        df['qtrs'] = df.qtrs.apply(int)
        df['value'] = pd.to_numeric(df['value'], errors='coerce')

        # die 'values' in den txt files haben maximal 4 nachkommastellen...
        df['value'] = df.value.round(4)

        df.loc[df.version == 'company', 'version'] = adsh

        df.drop(['segments','isrelevant'], axis=1, inplace=True)
        df.drop_duplicates(inplace=True)

        # set the indexes
        #df.set_index(['adsh', 'tag', 'version', 'ddate', 'qtrs'], inplace=True)
        df.set_index(['adsh', 'tag', 'version', 'ddate', 'qtrs', 'coreg', 'uom'], inplace=True)

        # and sort by the precision
        # it can happen that the same tag is represented in the reports multiple times with different precision
        # and it looks as if the "txt" data of the sec is then produced with the lower precision
        df.sort_values('decimals', inplace=True)
        df_double_index_mask = df.index.duplicated(keep='first')

        df = df[~df_double_index_mask]

        return df
