"""
Transforms the content on a "group" basis. Prepares data so that in the following processing step the
statement type (BS, IS, CF, ...) can be evaluated.
"""

import copy
from typing import Dict, List, Tuple

from secdaily._02_xml.parsing.pre._2_SecPreXmlTransformation import (
    SecPreTransformLocationDetails,
    SecPreTransformPresentationArcDetails,
    SecPreTransformPresentationDetails,
)


class SecPreXmlGroupTransformer:

    key_tag_separator = "$$$"

    # keywords of role definition that should be ignored
    role_report_ingore_keywords: List[str] = ["-note-", "supplemental", "-significant", "-schedule-", "role/disclosure"]

    def __init__(self):
        pass

    def _check_for_role_name_to_ignore(self, role: str) -> bool:
        role_lower = role.lower()
        for ignore_keyword in self.role_report_ingore_keywords:
            if ignore_keyword in role_lower:
                return True
        return False

    def _handle_digit_ending_case(
        self, preArc_list: List[SecPreTransformPresentationArcDetails], loc_list: List[SecPreTransformLocationDetails]
    ) -> Tuple[List[SecPreTransformPresentationArcDetails], List[SecPreTransformLocationDetails]]:
        """
        # a digit ending case has all labels ending with _<digits>, this case has to be handled especially, since
        # no hiearchy can be build. An example for this case is: 0000016160-21-000018
        # check for digit_ending
        example:
        <loc  label="Locator_us-gaap_StatementClassOfStockAxis_398"/>
        <presentationArc from="Locator_us-gaap_StatementClassOfStockAxis_403"
                         to="Locator_us-gaap_ClassOfStockDomain_404" order="1.0" preferredLabel="terseLabel"/>
        """
        digit_ending = True
        for loc in loc_list:
            digit_ending = digit_ending and loc.digit_ending

        # no digit_ending case, return list without processing
        if not digit_ending:
            return preArc_list, loc_list

        # a digit ending case is disjoint between from and to list
        to_list: List[str] = []
        from_list: List[str] = []

        for preArc in preArc_list:
            to_list.append(preArc.to_entry)
            from_list.append(preArc.from_entry)

        # if not disjoint, return preArc and loc lsit without processing
        if not set(to_list).isdisjoint(set(from_list)):
            return preArc_list, loc_list

        # this is a digit ending case:
        # therefore the _<digit> part has to be removed from the label
        # furthermore, every lable may appear only once in the loclist

        new_loc_list: List[SecPreTransformLocationDetails] = []
        new_loc_label_list: List[str] = []

        for loc in loc_list:
            new_loc = copy.copy(loc)
            label = loc.label
            label = label[: label.rfind("_")]
            new_loc.label = label

            if label in new_loc_label_list:
                continue
            new_loc_list.append(new_loc)
            new_loc_label_list.append(label)

        # in the preArc, the _<digit> part has to be removed from the from and to entries
        new_preArc_list: List[SecPreTransformPresentationArcDetails] = []
        for preArc in preArc_list:
            new_preArc = copy.copy(preArc)
            to_label = preArc.to_entry
            to_label = to_label[: to_label.rfind("_")]
            new_preArc.to_entry = to_label

            from_label = preArc.from_entry
            from_label = from_label[: from_label.rfind("_")]
            new_preArc.from_entry = from_label

            new_preArc_list.append(new_preArc)

        return new_preArc_list, new_loc_list

    def _handle_ambiguous_child_parent_relation(
        self, preArc_list: List[SecPreTransformPresentationArcDetails]
    ) -> List[SecPreTransformPresentationArcDetails]:
        # there are some rare cases (2 in 5500 reports from 2021-q1) when for a single node no line can be evaluated.
        # this is the reason when the child-parent relation is ambiguous.
        # e.g. "0001562762-21-000101" # StatementConsolidatedStatementsOfStockholdersEquity because there
        # in these cases, we have to kick out that entry and its children

        # these cases are identified, when a from node appears more than once in a two node
        to_list: List[str] = []
        from_list: List[str] = []

        for preArc in preArc_list:
            to_list.append(preArc.to_entry)
            from_list.append(preArc.from_entry)

        kick_out_list: List[str] = []

        # Find nodes that appear multiple times as child nodes (in to_list).
        # These indicate ambiguous parent-child relationships that need to be removed.
        for from_list_entry in from_list:
            count = sum(1 for x in to_list if x == from_list_entry)
            if count > 1:
                kick_out_list.append(from_list_entry)

        new_entries_found: bool = False

        # if a node has to be removed then also its children have to be removed. This recursive logic finds
        # all children, grandchildren, ... of nodes which have to be kicked-out as well
        while new_entries_found:
            new_entries_found = False
            for preArc in preArc_list:
                to_entry = preArc.to_entry
                from_entry = preArc.from_entry
                if from_entry in kick_out_list:
                    if to_entry not in kick_out_list:
                        kick_out_list.append(to_entry)
                        new_entries_found = True

        # now the entries can be removed from the orginial preArcList
        cleared_preArc_list: List[SecPreTransformPresentationArcDetails] = []

        for preArc in preArc_list:
            from_entry = preArc.from_entry
            if from_entry not in kick_out_list:
                cleared_preArc_list.append(preArc)

        return cleared_preArc_list

    def _calculate_key_tag_for_preArc(self, preArc_list: List[SecPreTransformPresentationArcDetails]):
        # the key_tag is needed in order to calculate the correct line number. it is necessary, since
        # it is possible that the same to_tag appears twice under different from_tags or (!) also the same from_tag.
        # but this seems to be only the case, if the to_tag is not also a from_tag.
        # therefore the keytag is the "to_tag" for the entries which have children (so they also appear in the from tag)
        # for the entries which don't have children, the keytag is the combination of from_tag, to_tag and order

        to_list: List[str] = []
        from_list: List[str] = []

        for preArc in preArc_list:
            to_list.append(preArc.to_entry)
            from_list.append(preArc.from_entry)

        for preArc in preArc_list:
            to_tag = preArc.to_entry
            from_tag = preArc.from_entry
            order_str = str(preArc.order_nr)

            if to_tag in from_list:
                key_tag = to_tag
            else:
                key_tag = to_tag + self.key_tag_separator + from_tag + self.key_tag_separator + order_str

            preArc.key_tag = key_tag

    def _find_root_node(self, preArc_list: List[SecPreTransformPresentationArcDetails]) -> str:
        """finds the root node, expect only ONE entry. If there is more than one root node, then an exception is raised
        and this report will be skipped later in the process."""
        to_list: List[str] = []
        from_list: List[str] = []

        for preArc in preArc_list:
            to_list.append(preArc.to_entry)
            from_list.append(preArc.from_entry)

        root_nodes = list(set(from_list) - set(to_list))

        # there should be just one rootnote, at least in the presentations we are interested in
        if len(root_nodes) != 1:
            return None

        return root_nodes[0]

    def grouptransform(
        self, data: Dict[int, SecPreTransformPresentationDetails]
    ) -> Dict[int, SecPreTransformPresentationDetails]:

        result: Dict[int, SecPreTransformPresentationDetails] = {}

        for idx, reportinfo in data.items():
            role: str = reportinfo.role
            loc_list: List[SecPreTransformLocationDetails] = reportinfo.loc_list
            preArc_list: List[SecPreTransformPresentationArcDetails] = reportinfo.preArc_list

            # no entries in node, so ignore
            if (len(preArc_list) == 0) or (len(loc_list) == 0):
                continue

            # there are some strings which indicate that this is not a report we are interested in
            if self._check_for_role_name_to_ignore(role):
                continue

            preArc_list, loc_list = self._handle_digit_ending_case(preArc_list, loc_list)
            preArc_list = self._handle_ambiguous_child_parent_relation(preArc_list)
            self._calculate_key_tag_for_preArc(preArc_list)

            reportinfo.preArc_list = preArc_list
            reportinfo.loc_list = loc_list
            reportinfo.root_node = self._find_root_node(preArc_list)

            result[idx] = reportinfo

        return result
