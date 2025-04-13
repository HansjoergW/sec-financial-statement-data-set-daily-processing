from typing import List, Tuple

import pandas as pd

from secdaily._02_xml.parsing.num._1_SecNumXmlExtracting import SecNumExtraction, SecNumXmlExtractor
from secdaily._02_xml.parsing.num._2_SecNumXmlTransformation import (
    SecNumTransformed,
    SecNumTransformedContext,
    SecNumTransformedTag,
    SecNumTransformedUnit,
    SecNumXmlTransformer,
)
from secdaily._02_xml.parsing.SecXmlParsingBase import ErrorEntry, SecXmlParserBase


class SecNumXmlParser(SecXmlParserBase):
    """Parses the data of an Num.Xml file and delivers the data in a similar format than the num.txt
    contained in the financial statements dataset of the sec."""

    def __init__(self):
        super().__init__("num")

    def _read_tags(self, adsh: str, transformed_data: SecNumTransformed) -> pd.DataFrame:

        entries = []
        tag: SecNumTransformedTag
        for tag in transformed_data.tag_list:

            context_entry: SecNumTransformedContext = transformed_data.contexts_map[tag.ctxtref]

            uom = None
            if tag.unitref is not None:
                unit_entry: SecNumTransformedUnit = transformed_data.units_map[tag.unitref]

                uom = unit_entry.uom
                # uom entries have a max length of 20
                uom = uom[: min(len(uom), 20)]

            decimals = tag.decimals
            if decimals:
                # decimal string contains often a -, but this leads to a wrong order if we want to compare as string
                decimals = decimals.replace("-", "")

                # sometimes INF is used instead of 0, which also indicates an  unrounded number
                if decimals == "INF":
                    decimals = "0"

            segments = context_entry.segments
            if len(segments) == 0:
                segments = None
            else:
                segments = ",".join([f"{segment.dimension}/{segment.label}" for segment in segments])

            temp_dict = {}
            temp_dict["adsh"] = adsh
            temp_dict["tag"] = tag.tagname
            temp_dict["version"] = tag.version
            temp_dict["uom"] = uom
            temp_dict["value"] = tag.valuetxt
            temp_dict["decimals"] = decimals
            temp_dict["ddate"] = context_entry.enddate
            temp_dict["qtrs"] = context_entry.qtrs
            temp_dict["segments"] = segments
            temp_dict["coreg"] = context_entry.coreg
            temp_dict["isrelevant"] = context_entry.isrelevant
            temp_dict["footnote"] = ""

            entries.append(temp_dict)

        return pd.DataFrame(entries)

    def parse(self, adsh: str, data: str) -> Tuple[pd.DataFrame, List[ErrorEntry]]:
        extractor: SecNumXmlExtractor = SecNumXmlExtractor()
        transformer: SecNumXmlTransformer = SecNumXmlTransformer()

        extracted_data: SecNumExtraction = extractor.extract(data=data)
        transformed_data: SecNumTransformed = transformer.transform(data=extracted_data)

        df = self._read_tags(adsh, transformed_data)
        return df, []


if __name__ == "__main__":
    example_file = "c:/ieu/projects/sec_processing/test/_02_xml/data/0001078782-21-000058-none-20201130.xml"
    with open(example_file, "r", encoding="utf-8") as f:
        xml_exp_content = f.read()
    f.close()

    parser = SecNumXmlParser()
    parsed_data, errors = parser.parse(adsh="0001078782-21-000058", data=xml_exp_content)
