from _02_xml.SecXmlParsingBase import SecXmlParserBase
from _02_xml.pre.SecPreXmlExtracting import SecPreXmlExtractor
from _02_xml.pre.SecPreXmlTransformation import SecPreXmlTransformer
from _02_xml.pre.SecPreXmlProcessing import SecPreXmlDataProcessor

import pandas as pd

from lxml import etree
from typing import Dict, List, Union
import pprint



class SecPreXmlParser(SecXmlParserBase):

    extractor: SecPreXmlExtractor  = SecPreXmlExtractor()
    transformer: SecPreXmlTransformer = SecPreXmlTransformer()
    processor: SecPreXmlDataProcessor = SecPreXmlDataProcessor()

    def __init__(self):
        super(SecPreXmlParser, self).__init__("pre")
        pass

    def parse(self, adsh:str, data: str) -> pd.DataFrame:

        extracted_data: Dict[int,Dict[str, Union[str, List[Dict[str, str]]]]] = self.extractor.extract(adsh, data)
        transformed_data: Dict[int, Dict[str, Union[str, List[Dict[str, str]]]]] = self.transformer.transform(adsh, extracted_data)
        processed_entries: List[Dict[str, Union[str, int]]] = self.processor.process(adsh, transformed_data)

        df = pd.DataFrame(processed_entries)
        df['rfile'] = '-'
        return df

    def clean_for_financial_statement_dataset(self, df: pd.DataFrame, adsh: str = None) -> pd.DataFrame:
        if len(df) == 0:
            return df
        df = df[~df.stmt.isnull()]
        df = df[df.line != 0].copy()
        df.drop(['plabel'], axis=1, inplace=True)
        df['adsh'] = adsh

        df.loc[df.version == 'company', 'version'] = adsh

        # we discovered, that comprehensive income statements are labelled as IS, if no IS is present.
        contained_statements = df.stmt.unique()
        if ("CI" in contained_statements) and ("IS" not in contained_statements):
            df.loc[df.stmt == 'CI', 'stmt'] = 'IS'

        df.set_index(['adsh', 'tag', 'version', 'report', 'line', 'stmt'], inplace=True)
        # print(adsh, ' - ', len(df))
        return df
