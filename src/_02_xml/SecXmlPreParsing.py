from _02_xml.SecXmlParsingBase import SecXmlParserBase, SecError
from _02_xml.pre.SecPreXmlExtracting import SecPreXmlExtractor, SecPreExtractPresentationLink
from _02_xml.pre.SecPreXmlTransformation import SecPreXmlTransformer, SecPreTransformPresentationDetails
from _02_xml.pre.SecPreXmlProcessing import SecPreXmlDataProcessor

import pandas as pd

from typing import Dict, List, Union, Tuple
import pprint


class SecPreXmlParser(SecXmlParserBase):

    def __init__(self):
        super(SecPreXmlParser, self).__init__("pre")
        pass

    def parse(self, adsh:str, data: str) -> Tuple[pd.DataFrame, List[SecError]]:
        extractor: SecPreXmlExtractor  = SecPreXmlExtractor()
        transformer: SecPreXmlTransformer = SecPreXmlTransformer()
        processor: SecPreXmlDataProcessor = SecPreXmlDataProcessor()

        extracted_data: Dict[int, SecPreExtractPresentationLink] = extractor.extract(adsh, data)
        transformed_data:  Dict[int, SecPreTransformPresentationDetails] = transformer.transform(adsh, extracted_data)

        processed_entries: List[Dict[str, Union[str, int]]]
        collected_errors: List[Tuple[str, str, str]]
        processed_entries, collected_errors = processor.process(adsh, transformed_data)

        sec_error_list = [SecError(x[0], x[1], x[2]) for x in collected_errors]

        # todo: use dataclasses asdict method to convert dataclasslist into dictionary, in case this pandas-version is not supporting dataclassed
        df = pd.DataFrame(processed_entries)
        df['rfile'] = '-'

        return (df, sec_error_list)

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
        return df
