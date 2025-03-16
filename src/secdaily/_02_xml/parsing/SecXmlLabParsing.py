

from typing import List, Tuple

import pandas as pd
from secdaily._02_xml.parsing.SecXmlParsingBase import SecError, SecXmlParserBase
from secdaily._02_xml.parsing.lab._1_SecLabXmlExtracting import SecLabXmlExtractor


class SecLabXmlParser(SecXmlParserBase):

    def __init__(self):
        super(SecLabXmlParser, self).__init__("lab"))
    

    def parse(self, adsh:str, data: str) -> Tuple[pd.DataFrame, List[SecError]]:
        
        extractor: SecLabXmlExtractor  = SecLabXmlExtractor()


        df = None
        sec_error_list = []
        return (df, sec_error_list)