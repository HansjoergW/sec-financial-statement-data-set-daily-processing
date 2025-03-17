from dataclasses import dataclass
from typing import List, Optional, Tuple
from secdaily._02_xml.parsing.lab._2_SecLabXmlTransformation import SecLabTransformLabelDetails

@dataclass
class LabelEntry:
    order: str
    from_entry: str
    to_entry: str
    terseLabel: Optional[str] = None
    positiveTerseLabel: Optional[str] = None
    label: Optional[str] = None
    positiveLabel: Optional[str] = None
    verboseLabel: Optional[str] = None
    documentation: Optional[str] = None
    negatedTerseLabel: Optional[str] = None
    negatedLabel: Optional[str] = None
    negatedVerboseLabel: Optional[str] = None
    periodStartLabel: Optional[str] = None
    negatedPeriodStartLabel: Optional[str] = None
    periodEndLabel: Optional[str] = None
    negatedPeriodEndLabel: Optional[str] = None
    totalLabel: Optional[str] = None
    negatedTotalLabel: Optional[str] = None
    netLabel: Optional[str] = None
    negatedNetLabel: Optional[str] = None


class SecLabXmlDataProcessor:

    def process(self, adsh: str, data: List[SecLabTransformLabelDetails]) -> Tuple[List[LabelEntry], List[Tuple[str, str, str]]]:

        result: List[LabelEntry] = []
        error_collector: List[Tuple[str, str, str]] = []

        for entry in data:
            try:
                label_entry = LabelEntry(
                    order=entry.order,
                    from_entry=entry.from_entry,
                    to_entry=entry.to_entry,
                    **entry.labels
                )
                result.append(label_entry)
            except Exception as e:
                error_collector.append((adsh, entry.to_entry, str(e)))

        return result, error_collector