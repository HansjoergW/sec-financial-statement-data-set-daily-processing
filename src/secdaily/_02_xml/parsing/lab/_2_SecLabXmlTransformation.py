from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List

from secdaily._02_xml.parsing.lab._1_SecLabXmlExtracting import SecLabLabelLink
from secdaily._02_xml.parsing.pre._2_SecPreXmlTransformation import SecPreXmlTransformer


@dataclass
class SecLabTransformLabelDetails:
    order: str
    from_entry: str
    to_entry: str
    tag: str
    version: str
    labels: defaultdict = field(default_factory=lambda: defaultdict(str))


class SecLabXmlTransformer:

    def transform(self, data: SecLabLabelLink) -> List[SecLabTransformLabelDetails]:

        us_eng_labels = [label for label in data.labels if label.lang == "en-US"]

        id_map: Dict[str, SecLabTransformLabelDetails] = {}

        loc_href_map: Dict[str, str] = {loc.label: loc.href for loc in data.locs}

        for arc in data.arcs:
            tag, version = SecPreXmlTransformer.get_version_tag_name_from_href(loc_href_map.get(arc.from_entry, ""))
            entry = SecLabTransformLabelDetails(
                order=arc.order, tag=tag, version=version, from_entry=arc.from_entry, to_entry=arc.to_entry
            )
            id_map[arc.to_entry] = entry

        for label in us_eng_labels:
            entry = id_map.get(label.label)
            if entry:
                entry.labels[label.role] = label.text

        return list(id_map.values())
