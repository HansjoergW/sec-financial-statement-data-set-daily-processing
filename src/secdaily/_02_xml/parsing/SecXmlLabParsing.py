

from typing import List, Tuple

import pandas as pd
from secdaily._02_xml.parsing.SecXmlParsingBase import SecError, SecXmlParserBase
from secdaily._02_xml.parsing.lab._1_SecLabXmlExtracting import SecLabLabelLink, SecLabXmlExtractor
from secdaily._02_xml.parsing.lab._2_SecLabXmlTransformation import SecLabXmlTransformer


class SecLabXmlParser(SecXmlParserBase):

    def __init__(self):
        super(SecLabXmlParser, self).__init__("lab")
    

    def parse(self, adsh:str, data: str) -> Tuple[pd.DataFrame, List[SecError]]:
        
        extractor: SecLabXmlExtractor  = SecLabXmlExtractor()
        transformer: SecLabXmlTransformer = SecLabXmlTransformer()

        extracted_data: SecLabLabelLink = extractor.extract(adsh, data)
        transformed_data: pd.DataFrame = transformer.transform(adsh, extracted_data)


        df = None
        sec_error_list = []
        return (df, sec_error_list)