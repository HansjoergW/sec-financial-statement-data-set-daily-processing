from secdaily._02_xml.parsing.SecXmlParsingBase import SecXmlParserBase, SecError
from secdaily._02_xml.parsing.pre._1_SecPreXmlExtracting import SecPreXmlExtractor, SecPreExtractPresentationLink
from secdaily._02_xml.parsing.pre._2_SecPreXmlTransformation import SecPreXmlTransformer, SecPreTransformPresentationDetails
from secdaily._02_xml.parsing.pre._3_SecPreXmlGroupTransformation import SecPreXmlGroupTransformer
from secdaily._02_xml.parsing.pre._4_SecPreXmlProcessing import SecPreXmlDataProcessor, PresentationEntry

import pandas as pd

from typing import Dict, List, Union, Tuple



class SecPreXmlParser(SecXmlParserBase):

    def __init__(self):
        super(SecPreXmlParser, self).__init__("pre")
        pass

    def parse(self, adsh:str, data: str) -> Tuple[pd.DataFrame, List[SecError]]:
        extractor: SecPreXmlExtractor  = SecPreXmlExtractor()
        transformer: SecPreXmlTransformer = SecPreXmlTransformer()
        grouptransformer: SecPreXmlGroupTransformer = SecPreXmlGroupTransformer()
        processor: SecPreXmlDataProcessor = SecPreXmlDataProcessor()

        extracted_data: Dict[int, SecPreExtractPresentationLink] = extractor.extract(adsh, data)
        transformed_data: Dict[int, SecPreTransformPresentationDetails] = transformer.transform(adsh, extracted_data)
        group_transformed_data: Dict[int, SecPreTransformPresentationDetails] = grouptransformer.grouptransform(adsh, transformed_data)

        processed_entries: List[PresentationEntry]
        collected_errors: List[Tuple[str, str, str]]
        processed_entries, collected_errors = processor.process(adsh, group_transformed_data)

        sec_error_list = [SecError(x[0], x[1], x[2]) for x in collected_errors]

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
        # attention: inpth has o be considered
        contained_statements = df[df.inpth==0].stmt.unique()
        if ("CI" in contained_statements) and ("IS" not in contained_statements):
            df.loc[(df.stmt == 'CI') & (df.inpth==0), 'stmt'] = 'IS'

            contained_statements_inpth = df[df.inpth==1].stmt.unique()
            if ("CI" in contained_statements_inpth) and ("IS" not in contained_statements_inpth):
                df.loc[(df.stmt == 'CI') & (df.inpth==1), 'stmt'] = 'IS'

        df.set_index(['adsh', 'tag', 'version', 'report', 'line', 'stmt'], inplace=True)
        return df
