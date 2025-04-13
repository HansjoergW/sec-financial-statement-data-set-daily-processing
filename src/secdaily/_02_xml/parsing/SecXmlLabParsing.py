from typing import List, Tuple

import pandas as pd

from secdaily._02_xml.parsing.lab._1_SecLabXmlExtracting import SecLabLabelLink, SecLabXmlExtractor
from secdaily._02_xml.parsing.lab._2_SecLabXmlTransformation import SecLabTransformLabelDetails, SecLabXmlTransformer
from secdaily._02_xml.parsing.lab._3_SecLabXmlProcessing import LabelEntry, SecLabXmlDataProcessor
from secdaily._02_xml.parsing.SecXmlParsingBase import ErrorEntry, SecXmlParserBase


class SecLabXmlParser(SecXmlParserBase):

    def __init__(self):
        super().__init__("lab")

    def parse(self, adsh: str, data: str) -> Tuple[pd.DataFrame, List[ErrorEntry]]:

        extractor: SecLabXmlExtractor = SecLabXmlExtractor()
        transformer: SecLabXmlTransformer = SecLabXmlTransformer()
        processor: SecLabXmlDataProcessor = SecLabXmlDataProcessor()

        extracted_data: SecLabLabelLink = extractor.extract(data=data)
        transformed_data: List[SecLabTransformLabelDetails] = transformer.transform(data=extracted_data)
        processed_entries: List[LabelEntry]
        collected_errors: List[Tuple[str, str, str]]
        processed_entries, collected_errors = processor.process(adsh, transformed_data)

        sec_error_list = [ErrorEntry(adsh=x[0], error_info=x[1], error=x[2]) for x in collected_errors]

        df = pd.DataFrame(processed_entries)

        return (df, sec_error_list)
