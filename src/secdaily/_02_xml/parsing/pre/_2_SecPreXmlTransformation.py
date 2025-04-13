import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from secdaily._02_xml.parsing.pre._1_SecPreXmlExtracting import (
    SecPreExtractLocationDetails,
    SecPreExtractPresentationArcDetails,
    SecPreExtractPresentationLink,
)


@dataclass
class SecPreTransformLocationDetails:
    label: str
    tag: str
    version: str
    digit_ending: bool


@dataclass
class SecPreTransformPresentationArcDetails:
    negating: bool
    order_nr: float
    preferredLabel: str
    from_entry: str
    to_entry: str
    key_tag: Optional[str] = None
    line: Optional[int] = None


@dataclass
class SecPreTransformPresentationDetails:
    loc_list: List[SecPreTransformLocationDetails]
    preArc_list: List[SecPreTransformPresentationArcDetails]
    title: str
    role: str
    inpth: str
    root_node: Optional[str] = None


class SecPreXmlTransformer:
    digit_ending_label_regex = re.compile(r"_\d*$")

    @staticmethod
    def get_version_tag_name_from_href(href: str) -> Tuple[str, str]:
        # Attention: extend testcases if adaptions should be necessary.

        # in the href-definition, the first part indicates wich namespace and version it, if they start with http:
        # eg: xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_AccountingStandardsUpdate201802Member" pylint: disable=line-too-long
        # if it is a company namespace, then there is no http:
        # eg: xlink:href="pki-20210103.xsd#pki_AccountingStandardsUpdate_201616Member"
        # if it is a "company", then the version of the tag is the adsh number of the report
        # otherwise, the year and namespace is extracted from the namespace path.
        # the used "tag" itself follows after the hash, without the content before the first "_"
        # eg: us-gaap_AccountingStandardsUpdate201802Member -> AccountingStandardsUpdate201802Member
        # eg: pki_AccountingStandardsUpdate_201616Member    -> AccountingStandardsUpdate_201616Member
        # Note
        # tags kann have '_' in their name

        href_parts = href.split("#")
        complete_tag = href_parts[1]
        version: Optional[str] = None
        if href_parts[0].startswith("http"):
            ns_parts = href_parts[0].split("/")
            version = ns_parts[3] + "/" + ns_parts[4]
        else:
            version = "company"  # special hint to indicate that this is a company specifig tag

        pos = complete_tag.find("_")
        tag = complete_tag[pos + 1 :]

        return tag, version

    def _transform_loc(
        self, extract_loc_list: List[SecPreExtractLocationDetails]
    ) -> List[SecPreTransformLocationDetails]:
        result: List[SecPreTransformLocationDetails] = []
        for extract_loc in extract_loc_list:
            tag, version = SecPreXmlTransformer.get_version_tag_name_from_href(extract_loc.href)
            transform_loc = SecPreTransformLocationDetails(
                label=extract_loc.label, tag=tag, version=version, digit_ending=False
            )

            # there are some special cases of reports which adds a running number to every appereance of a label,
            # also in the to and from attributes of the preArc entries (e.g. 0000016160-21-000018).
            # (like '...._12'). This makes it impossible to build up the hierarchy and therefore to find the root.
            # therefore, this labels have to handled in a special way
            if self.digit_ending_label_regex.search(extract_loc.label):
                transform_loc.digit_ending = True

            result.append(transform_loc)
        return result

    def _transform_preArc(
        self, extract_preArc_list: List[SecPreExtractPresentationArcDetails]
    ) -> List[SecPreTransformPresentationArcDetails]:
        result: List[SecPreTransformPresentationArcDetails] = []

        for extract_preArc in extract_preArc_list:
            # figure out wether the preferredLabel gives a  hint that the displayed number is inverted
            negated: bool = "negated" in extract_preArc.preferredLabel

            transform_presentationArc = SecPreTransformPresentationArcDetails(
                to_entry=extract_preArc.to_entry,
                from_entry=extract_preArc.from_entry,
                preferredLabel=extract_preArc.preferredLabel,
                negating=negated,
                # some xmls use 0.0, 1.0 ... as order number instead of a pure int, so we ensure that we have an
                # order_nr that is always a float
                # there are also strange entries which have an order number of xy.02 or similar
                order_nr=float(extract_preArc.order),
            )

            result.append(transform_presentationArc)

        return result

    def transform(
        self, data: Dict[int, SecPreExtractPresentationLink]
    ) -> Dict[int, SecPreTransformPresentationDetails]:

        result: Dict[int, SecPreTransformPresentationDetails] = {}
        for k, v in data.items():
            entry = SecPreTransformPresentationDetails(
                loc_list=self._transform_loc(v.loc_list),
                preArc_list=self._transform_preArc(v.preArc_list),
                title=v.title,
                role=v.role,
                inpth="0",
            )

            # if there is a title info, then this has precedence over the role
            if entry.title is not None:
                entry.role = entry.title

            # figure out if data in a report where contained in parenthesis
            if "parenthetical" in entry.role.lower():
                entry.inpth = "1"

            result[k] = entry
        return result
