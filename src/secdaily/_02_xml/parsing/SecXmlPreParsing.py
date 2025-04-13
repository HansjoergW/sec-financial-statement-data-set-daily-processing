from typing import Dict, List, Tuple

import pandas as pd

from secdaily._02_xml.parsing.pre._1_SecPreXmlExtracting import SecPreExtractPresentationLink, SecPreXmlExtractor
from secdaily._02_xml.parsing.pre._2_SecPreXmlTransformation import (
    SecPreTransformPresentationDetails,
    SecPreXmlTransformer,
)
from secdaily._02_xml.parsing.pre._3_SecPreXmlGroupTransformation import SecPreXmlGroupTransformer
from secdaily._02_xml.parsing.pre._4_SecPreXmlProcessing import PresentationEntry, SecPreXmlDataProcessor
from secdaily._02_xml.parsing.SecXmlParsingBase import ErrorEntry, SecXmlParserBase


class SecPreXmlParser(SecXmlParserBase):

    def __init__(self):
        super().__init__("pre")

    def parse(self, adsh: str, data: str) -> Tuple[pd.DataFrame, List[ErrorEntry]]:
        extractor: SecPreXmlExtractor = SecPreXmlExtractor()
        transformer: SecPreXmlTransformer = SecPreXmlTransformer()
        grouptransformer: SecPreXmlGroupTransformer = SecPreXmlGroupTransformer()
        processor: SecPreXmlDataProcessor = SecPreXmlDataProcessor()

        extracted_data: Dict[int, SecPreExtractPresentationLink] = extractor.extract(data=data)
        transformed_data: Dict[int, SecPreTransformPresentationDetails] = transformer.transform(data=extracted_data)
        group_transformed_data: Dict[int, SecPreTransformPresentationDetails] = grouptransformer.grouptransform(
            data=transformed_data
        )

        processed_entries: List[PresentationEntry]
        collected_errors: List[Tuple[str, str, str]]
        processed_entries, collected_errors = processor.process(adsh, group_transformed_data)

        sec_error_list = [ErrorEntry(x[0], x[1], x[2]) for x in collected_errors]

        df = pd.DataFrame(processed_entries)
        df["rfile"] = "-"

        return (df, sec_error_list)
