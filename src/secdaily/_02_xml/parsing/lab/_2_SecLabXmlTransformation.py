
from typing import Dict
from collections import defaultdict
from dataclasses import dataclass, field
from typing import List
from secdaily._02_xml.parsing.lab._1_SecLabXmlExtracting import SecLabLabelLink




@dataclass
class SecLabTransformLabelDetails():
    order: str
    from_entry: str
    to_entry: str
    labels: defaultdict = field(default_factory=lambda: defaultdict(str))

    @staticmethod
    def is_labelrole_supported(labelrole: str) -> bool:
        return labelrole in [
            "terseLabel",
            "positiveTerseLabel",
            "label",
            "positiveLabel",
            "verboseLabel",
            "documentation",
            "negatedTerseLabel",
            "negatedLabel",
            "negatedVerboseLabel",
            "periodStartLabel",
            "negatedPeriodStartLabel",
            "periodEndLabel",
            "negatedPeriodEndLabel",
            "totalLabel",
            "negatedTotalLabel"
        ]


class SecLabXmlTransformer:

    def transform(self, adsh: str, data: SecLabLabelLink) -> List[SecLabTransformLabelDetails]:

        us_eng_labels = [label for label in data.labels if label.lang == "en-US"]

        id_map: Dict[str, SecLabTransformLabelDetails] = {}

        for arc in data.arcs:
            entry = SecLabTransformLabelDetails(
                order=arc.order,
                from_entry=arc.from_entry,
                to_entry=arc.to_entry)
            id_map[arc.to_entry] = entry
            
    
        for label in us_eng_labels:
            entry = id_map.get(label.label)
            if entry and SecLabTransformLabelDetails.is_labelrole_supported(label.role):
                entry.labels[label.role] = label.text

        return list(id_map.values())
    
    
