from dataclasses import dataclass
from typing import List, Optional, Tuple
from secdaily._02_xml.parsing.lab._2_SecLabXmlTransformation import SecLabTransformLabelDetails

@dataclass
class LabelEntry:
    key: str
    to_entry: str
    label: Optional[str]


class SecLabXmlDataProcessor:

    def process(self, adsh: str, data: List[SecLabTransformLabelDetails]) -> Tuple[List[LabelEntry], List[Tuple[str, str, str]]]:

        result: List[LabelEntry] = []
        error_collector: List[Tuple[str, str, str]] = []

        for entry in data:
            for type, text in entry.labels.items():
                key = f"{entry.from_entry}#{type}"
                try:
                    label_entry = LabelEntry(
                        key=key,
                        to_entry=entry.to_entry,
                        label=text
                    )
                    result.append(label_entry)
                except Exception as e:
                    error_collector.append((adsh, key, str(e)))

        return result, error_collector