import logging
from dataclasses import dataclass
from typing import Dict, List, Tuple

from secdaily._02_xml.parsing.pre._2_SecPreXmlTransformation import (
    SecPreTransformLocationDetails,
    SecPreTransformPresentationArcDetails,
    SecPreTransformPresentationDetails,
)
from secdaily._02_xml.parsing.pre._4_1_SecPreXmlStatementTypeEvaluation import (
    SecPreXmlStatementTypeEvaluator,
    StmtConfidence,
)


@dataclass
class PresentationEntry:
    version: str
    tag: str
    plabel: str
    negating: bool
    line: int
    stmt: str = None
    inpth: int = None
    report: int = None


@dataclass
class PresentationReport:
    adsh: str
    role: str
    loc_list: List[SecPreTransformLocationDetails]
    preArc_list: List[SecPreTransformPresentationArcDetails]
    rootNode: str
    entries: List[PresentationEntry]
    inpth: int
    stmt_canditates: Dict[str, StmtConfidence]


class SecPreXmlDataProcessor:
    """
    processes the extracted and transformed data from a prexml file
    """

    def __init__(self):
        pass

    def _calculate_line_nr(self, root_node: str, preArc_list: List[SecPreTransformPresentationArcDetails]):
        """the 'only' thing this method does is to add the 'line' attribute to the preArc entries.
        this is done 'inplace'"""

        # building parent child relation from the from and to attributes of the preArc entries
        parent_child_dict: Dict[str, Dict[float, str]] = {}
        preArc_by_keytag_dict: Dict[str, SecPreTransformPresentationArcDetails] = {}
        for preArc in preArc_list:
            order_nr = preArc.order_nr
            key_tag = preArc.key_tag
            from_tag = preArc.from_entry

            if from_tag not in parent_child_dict:
                parent_child_dict[from_tag] = {}

            parent_child_dict[from_tag][order_nr] = key_tag
            preArc_by_keytag_dict[key_tag] = preArc

        # the problem with the order number is, that the usage is not consistent.
        # in some reports, every child node starts with zero, in others, it starts with 1.
        # sometimes that is even mixed within the same presentation link.
        # example (temir-20200831_pre.xml)
        # other reports use a unique order number inside the presentation. (like gbt-20201231_pre.xml)
        # in this case, this would directly reflect the line number which would be the most simple way to calculate.
        # so we first need to convert that in a simple ordered list which follows the defined order
        parent_child_ordered_list: Dict[str, List[str]] = {}
        for node_name, order_dict in parent_child_dict.items():
            child_list: List[str] = []
            for childkey in sorted(order_dict.keys()):
                child_list.append(order_dict.get(childkey))
            parent_child_ordered_list[node_name] = child_list

        # in order to calculate the line numbers, it is necessary walk along the parent-child relationship of the
        # presentation-arc while respecting the order number and starting with the root_node
        # in order to that, a recursive loop is used
        node_path: List[str] = [root_node]  # used to track the path

        # used to keep track of current processed child of these node
        # the problem is, that in some documents the order starts with a 0, in others with 1
        # in some documents, this is even mixed within the same presentation, so we need to figure out
        # what the start key is
        node_index: Dict[str, int] = {root_node: 0}

        line = 1
        while len(node_path) > 0:
            current_node = node_path[-1]
            current_index = node_index.get(current_node)
            current_children_ordered_list = parent_child_ordered_list[current_node]

            if current_index + 1 > len(current_children_ordered_list):
                node_path.pop()
                continue

            node_index[current_node] = current_index + 1

            child = current_children_ordered_list[current_index]

            preArc_by_keytag_dict[child].line = line

            grand_children = parent_child_ordered_list.get(child)
            if grand_children is not None:
                node_path.append(child)
                node_index[child] = 0

            line += 1

    def _calculate_entries(
        self,
        loc_list: List[SecPreTransformLocationDetails],
        preArc_list: List[SecPreTransformPresentationArcDetails],
    ) -> List[PresentationEntry]:

        # create dict by label for the loc-entries, so that we can link them to with the preArc entries
        loc_by_label_dict: Dict[str, SecPreTransformLocationDetails] = {}
        for loc in loc_list:
            label = loc.label
            loc_by_label_dict[label] = loc

        result: List[PresentationEntry] = []
        for preArc in preArc_list:
            to_tag = preArc.to_entry

            loc_entry = loc_by_label_dict[to_tag]
            entry = PresentationEntry(
                version=loc_entry.version,
                tag=loc_entry.tag,
                plabel=preArc.preferredLabel,
                negating=preArc.negating,
                line=preArc.line,
            )

            result.append(entry)

        return result

    def process_reports(
        self, adsh: str, data: Dict[int, SecPreTransformPresentationDetails]
    ) -> Tuple[Dict[int, PresentationReport], List[Tuple[str, str, str]]]:
        # processed the reports in the data.
        # organizes the reports by the report-type (BS, CP, CI, IS, CF, EQ) in the result

        # result is a dictionary with the chosen stmt as key and a list of the reports as Dicts
        result: Dict[int, PresentationReport] = {}
        error_collector: List[Tuple[str, str, str]] = []
        stmt_evaluator = SecPreXmlStatementTypeEvaluator()

        for idx, reportinfo in data.items():
            role: str = reportinfo.role
            inpth: int = int(reportinfo.inpth)
            loc_list: List[SecPreTransformLocationDetails] = reportinfo.loc_list
            preArc_list: List[SecPreTransformPresentationArcDetails] = reportinfo.preArc_list
            root_node: str = reportinfo.root_node

            stmt_canditates: Dict[str, StmtConfidence] = stmt_evaluator.evaluate_statement_canditates(
                role, root_node, loc_list
            )
            if root_node is None:
                error_collector.append((adsh, role, str("Not a single root node found")))
                # just log if the name gives a hint that this could be a primary statement
                if len(stmt_canditates) > 0:
                    logging.warning(
                        "%s / %s skipped report with role %s : Not a single root node found",
                        adsh,
                        list(stmt_canditates.keys()),
                        role,
                    )
                continue

            if len(stmt_canditates) == 0:
                continue

            try:
                self._calculate_line_nr(root_node, preArc_list)
                entries: List[PresentationEntry] = self._calculate_entries(loc_list=loc_list, preArc_list=preArc_list)

                report = PresentationReport(
                    adsh=adsh,  # str
                    role=role,  # str
                    loc_list=loc_list,  # List[SecPreTransformLocationDetails]
                    preArc_list=preArc_list,  # List[SecPreTransformPresentationArcDetails]
                    rootNode=root_node,  # str
                    entries=entries,  # List[PresentationEntry]
                    inpth=inpth,  # int
                    stmt_canditates=stmt_canditates,  # Dict[str, StmtConfidence]
                )
                result[idx] = report

            except Exception as err:  # pylint: disable=broad-except
                error_collector.append((adsh, role, str(err)))

        return (result, error_collector)

    def _post_process_assign_report_to_stmt(
        self, report_data: Dict[int, PresentationReport]
    ) -> Dict[Tuple[str, int], List[PresentationReport]]:
        # based on the stmt_canditates info, this function figures out to which statement type the report belongs to.
        # generally, there should be just one possiblity

        # the key is defined from the stmt type ('BS', 'IS', ..) the flog "inpth"
        # which indicates wether it is  a "in parenthical" report
        result: Dict[Tuple[str, int], List[PresentationReport]] = {}

        # ensure that a report only belongs to one stmt type
        for _, reportinfo in report_data.items():
            stmt_canditates_dict: Dict[str, StmtConfidence] = reportinfo.stmt_canditates
            stmt_canditates_keys = list(stmt_canditates_dict.keys())
            inpth = reportinfo.inpth

            stmt: str
            if len(stmt_canditates_keys) == 1:
                stmt = stmt_canditates_keys[0]
            else:
                # try to either find a single confidence of 2
                # or to find the entry with the biggest sum of confidence values

                max_sum_of_confidence = 0
                max_sum_of_confidence_stmt = None

                for stmt_key in stmt_canditates_keys:
                    confidence: StmtConfidence = stmt_canditates_dict[stmt_key]

                    sum_of_confidence = confidence.get_confidence_sum()
                    if sum_of_confidence > max_sum_of_confidence:
                        max_sum_of_confidence = sum_of_confidence
                        max_sum_of_confidence_stmt = stmt_key

                stmt = max_sum_of_confidence_stmt

            if result.get((stmt, inpth)) is None:
                result[(stmt, inpth)] = []

            result[(stmt, inpth)].append(reportinfo)

        return result

    def _post_process_cp(self, stmt_list: List[PresentationReport]) -> List[PresentationReport]:
        # in all the reports, there was always just on CP entry
        # so we either return the first who was identified as CP by the rolename
        # or we return the first entry of the list (since CP is generally the first that appears in a report)
        for report_data in stmt_list:
            confidence_dict = report_data.stmt_canditates["CP"]
            if confidence_dict.byRole == 2:
                return [report_data]
        first_entry = stmt_list[0]
        return [first_entry]

    def _post_process_general(self, stmt_type: str, stmt_list: List[PresentationReport]) -> List[PresentationReport]:
        """
        often detail-reports contain the keywords in their role definition but also much more text.
        there are also cases with proper supparts of a company like 0001711269-21-000023

        """
        current_max_confidence = 0
        current_max_confidence_list: List[PresentationReport] = []

        for report_data in stmt_list:
            confidence = report_data.stmt_canditates[stmt_type]

            sum_confidence = confidence.get_confidence_sum()
            if sum_confidence > current_max_confidence:
                current_max_confidence = sum_confidence
                current_max_confidence_list = []
            if sum_confidence == current_max_confidence:
                current_max_confidence_list.append(report_data)

        # at max, one bs report for either with or without the inpth (in parentical) flag is returned
        # if there are more, then the ones with the shortest "role" are returned
        shortest_bs = None
        for entry in current_max_confidence_list:
            role = entry.role

            if (shortest_bs is None) or (len(role) < len(shortest_bs.role)):
                shortest_bs = entry

        result: List[PresentationReport] = []
        if shortest_bs is not None:
            result.append(shortest_bs)

        return result

    def _post_process_is(
        self, stmt_type: str, inpth: int, stmt_list: List[PresentationReport]
    ) -> List[PresentationReport]:

        result: List[PresentationReport] = self._post_process_general(stmt_type, stmt_list)

        # just the label hint is not enough for IS
        if (inpth == 0) and (result[0].stmt_canditates["IS"].get_confidence_sum() == 1):
            return []

        return result

    def _post_process_ci(
        self, stmt_type: str, inpth: int, stmt_list: List[PresentationReport]
    ) -> List[PresentationReport]:

        if inpth == 1:
            return self._post_process_general(stmt_type, stmt_list)

        # ignore only by label
        not_only_by_label: List[PresentationReport] = []
        role_conf_3: List[PresentationReport] = []
        max_role: int = 0

        for report in stmt_list:
            if report.stmt_canditates["CI"].get_confidence_sum() > 1:
                not_only_by_label.append(report)
            if (report.stmt_canditates["CI"].byRole == 3) and (report.stmt_canditates["CI"].get_confidence_sum() > 3):
                role_conf_3.append(report)
            max_role = max(max_role, report.stmt_canditates["CI"].byRole)

        # in case max_role > 3 or  not more than 1 role with conf 3
        #  -> the standard in general approach can be used
        if (max_role > 3) or (len(role_conf_3) < 2):
            return self._post_process_general(stmt_type, stmt_list)

        # if there is more than one entry with byrole confidence of 3, we take the one with the most labels!
        # case: 0000766704-21-000018 -> actually two valid CIs entries > first is an IS with comprehensive Tag
        # we just return the first two, there shoudln't be more

        return role_conf_3[:2]

    def process(
        self, adsh: str, data: Dict[int, SecPreTransformPresentationDetails]
    ) -> Tuple[List[PresentationEntry], List[Tuple[str, str, str]]]:

        results: List[PresentationEntry] = []

        report_data: Dict[int, PresentationReport]
        error_collector: List[Tuple[str, str, str]]

        report_data, error_collector = self.process_reports(adsh, data)

        stmt_data: Dict[Tuple[str, int], List[PresentationReport]] = self._post_process_assign_report_to_stmt(
            report_data
        )

        reportnr = 0

        selected: Dict[Tuple[str, int], List[PresentationReport]] = {}
        for stmtkey, stmt_list in stmt_data.items():
            stmt, inpth = stmtkey

            if stmt == "CP":
                stmt_list = self._post_process_cp(stmt_list)

            if stmt == "BS":
                stmt_list = self._post_process_general("BS", stmt_list)

            if stmt == "IS":
                stmt_list = self._post_process_is("IS", inpth, stmt_list)

            if stmt == "CI":
                stmt_list = self._post_process_ci("CI", inpth, stmt_list)

            if stmt == "CF":
                stmt_list = self._post_process_general("CF", stmt_list)

            selected[stmtkey] = stmt_list

            for report in stmt_list:
                entries: List[PresentationEntry] = report.entries
                reportnr += 1
                for entry in entries:
                    entry.report = reportnr
                    entry.inpth = inpth

        if (len(selected.get(("CI", 0), [])) > 1) and (len(selected.get(("IS", 0), [])) == 0):
            # case 3.12 / 0000766704-21-000018
            # falls zwei CIs und kein IS, CI mit mehr labels wird zum IS
            # wird übersteuert, ohne Berücksichtigung von inpth

            ci_reports = selected[("CI", 0)]
            max_label_count: int = 0

            for report in ci_reports:
                max_label_count = max(max_label_count, len(report.loc_list))

            for report in ci_reports:
                if len(report.loc_list) == max_label_count:
                    selected[("IS", 0)] = [report]
                else:
                    selected[("CI", 0)] = [report]

        for stmtkey, stmt_list in selected.items():
            stmt, inpth = stmtkey

            for report in stmt_list:
                entries: List[PresentationEntry] = report.entries
                reportnr += 1
                for entry in entries:
                    entry.stmt = stmt

                results.extend(entries)

        return (results, error_collector)
