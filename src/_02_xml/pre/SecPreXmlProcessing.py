from _02_xml.pre.SecPreXmlTransformation import SecPreTransformPresentationDetails, \
    SecPreTransformPresentationArcDetails, SecPreTransformLocationDetails
from typing import Dict, Union, List, Tuple, Set
import logging
import copy
import pprint as pp

from dataclasses import dataclass


@dataclass
class EvalEntry:
    includes: List[str]
    excludes: List[str]
    confidence: int = 0


@dataclass
class StmtEvalDefinition:
    role_keys: List[EvalEntry]
    root_keys: List[EvalEntry]
    label_list: List[EvalEntry]


@dataclass
class StmtConfidence:
    byRole: int
    byRoot: int
    byLabel: int

    def get_max_confidenc(self):
        return max(self.byRole, self.byRoot, self.byLabel)

    def get_confidence_sum(self):
        return self.byLabel + self.byRole + self.byRole


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

    # confidence of 2 is max
    # # stmt
    #     role_keys: [{includes, excludes, confidence}]
    #     root_keys
    #     label_list -> evtll noch mit versionliste und tagliste unterscheiden

    stmt_eval_dict = {
        'CP': StmtEvalDefinition(
            role_keys=[
                EvalEntry(
                    includes=['role/cover'],
                    excludes=[],
                    confidence=2),
                EvalEntry(
                    includes=['coverpage'],
                    excludes=[],
                    confidence=2),
                EvalEntry(
                    includes=['coverabstract'],
                    excludes=[],
                    confidence=2),
                EvalEntry(
                    includes=['deidocument'],
                    excludes=[],
                    confidence=2),
                EvalEntry(
                    includes=['document', 'entity', 'information'],
                    excludes=[],
                    confidence=2),
            ],
            root_keys=[
                EvalEntry(
                    includes=['document', 'entity', 'information'],
                    excludes=[],
                    confidence=2),
                EvalEntry(
                    includes=['coverpage'],
                    excludes=[],
                    confidence=2),
                EvalEntry(
                    includes=['coverabstract'],
                    excludes=[],
                    confidence=2),
            ],
            label_list=[]
        ),

        'BS': StmtEvalDefinition(
            role_keys=[
                EvalEntry(
                    includes=['consolidated', 'statement', 'financialposition'],
                    excludes=['detail'],
                    confidence=2),
                EvalEntry(
                    includes=['consolidated', 'statement', 'financialcondition'],
                    excludes=['detail'],
                    confidence=2),
                EvalEntry(
                    includes=['consolidated', 'statement', 'condition'],
                    excludes=['detail'],
                    confidence=2),
                EvalEntry(
                    includes=['consolidated', 'balance', 'sheet'],
                    excludes=['detail'],
                    confidence=2),
                EvalEntry(
                    includes=['condensed', 'balance', 'sheet'],
                    excludes=['detail'],
                    confidence=2),
                EvalEntry(
                    includes=['statement', 'balance', 'sheet'],
                    excludes=['detail'],
                    confidence=2),
                EvalEntry(
                    includes=['statement', 'financialposition'],
                    excludes=['detail'],
                    confidence=2),
                EvalEntry(
                    includes=['statement', 'financialcondition'],
                    excludes=['detail'],
                    confidence=2),
                EvalEntry(
                    includes=['statement', 'condition'],
                    excludes=['detail'],
                    confidence=2),
                EvalEntry(
                    includes=['statement', 'assets', 'liabilities'],
                    excludes=['detail'],
                    confidence=2),
                EvalEntry(
                    includes=['role/balancesheet'],
                    excludes=['detail'],
                    confidence=2),
                EvalEntry(
                    # special case for "arma.com": ex. 0001625285-21-000004, 0001625285-21-000002,  0001625285-21-000006
                    includes=['role/idr_balancesheet'],
                    excludes=['detail'],
                    confidence=2),
                EvalEntry(  # special case for "kingsway" only report with details in main BS 0001072627-21-000022
                    includes=['kingsway-financial', 'consolidated', 'balancesheet'],
                    excludes=[],
                    confidence=2),
                EvalEntry(  # special case for xfleet BS with role cashflow 0001213900-21-019311
                    includes=['www.xlfleet.com', 'consolidatedcashflow'],
                    excludes=['cashflow0'],
                    confidence=2),
            ],
            root_keys=[
                EvalEntry(
                    includes=['statementoffinancialposition'],
                    excludes=[],
                    confidence=1),
                EvalEntry(
                    includes=['balancesheet', 'parenthetical'],
                    excludes=[],
                    confidence=1),
            ],
            label_list=[]),

        'EQ': StmtEvalDefinition(
            role_keys=[
                EvalEntry(
                    includes=['statement', 'shareholder', 'equity'],
                    excludes=[],
                    confidence=2),
                EvalEntry(
                    includes=['statement', 'stockholder', 'equity'],
                    excludes=[],
                    confidence=2),
                EvalEntry(
                    includes=['statement', 'shareowner', 'equity'],
                    excludes=[],
                    confidence=2),
                EvalEntry(
                    includes=['statement', 'stockowner', 'equity'],
                    excludes=[],
                    confidence=2),
            ],
            root_keys=[],
            label_list=[]
        ),

        'IS': StmtEvalDefinition(
            role_keys=[
                EvalEntry(
                    includes=['consolidated', 'statement', 'income'],
                    excludes=['comprehensive'],
                    confidence=2),
                EvalEntry(
                    includes=['consolidated', 'statement', 'operation'],
                    excludes=['comprehensive'],
                    confidence=2),
                EvalEntry(
                    includes=['condensed', 'statement', 'operation'],
                    excludes=['detail'],
                    confidence=2),
                EvalEntry(
                    includes=['statement', 'operation'],
                    excludes=['comprehensive'],
                    confidence=2),
            ],
            root_keys=[
                EvalEntry(
                    includes=['income', 'statement', 'abstract'],
                    excludes=['comprehensive'],
                    confidence=1),
            ],
            label_list=[
                EvalEntry(
                    includes=[],
                    excludes=['comprehensiveincome'],
                    confidence=1
                )
            ]
        ),

        'CI': StmtEvalDefinition(
            role_keys=[
                EvalEntry(
                    includes=['comprehensive', 'consolidated', 'statement', 'income'],
                    excludes=[],
                    confidence=2),
                EvalEntry(
                    includes=['comprehensive', 'consolidated', 'statement', 'operation'],
                    excludes=[],
                    confidence=2),
            ],
            root_keys=[
                EvalEntry(
                    includes=['comprehensive', 'income', 'statement', 'abstract'],
                    excludes=[],
                    confidence=1),
            ],
            label_list=[
                EvalEntry(
                    includes=['comprehensiveincome'],
                    excludes=[],
                    confidence=1
                )
            ]
        ),

        'CF': StmtEvalDefinition(
            role_keys=[
                EvalEntry(
                    includes=['consolidated', 'statement', 'cashflow'],
                    excludes=[],
                    confidence=2),
                EvalEntry(
                    includes=['condensed', 'statement', 'cashflow'],
                    excludes=[],
                    confidence=2),

            ],

            # SonderFall für diesen hier kann man nicht so einfach excluden...
            # ginge nur über labels oder mit regex prüfung
            # { # special case for xfleet BS with role cashflow 0001213900-21-019311
            #     includes= ['www.xlfleet.com', 'consolidatedcashflow'],
            #     excludes= ['cashflow0'],
            #     confidence= 2
            # },

            root_keys=[],
            label_list=[]
        )
    }

    # keywords of role definition that should be ignored
    role_report_ingore_keywords: List[str] = ['-note-', 'supplemental', '-significant', '-schedule-']

    key_tag_separator = '$$$'

    def __init__(self):
        pass

    def _handle_digit_ending_case(self, preArc_list: List[SecPreTransformPresentationArcDetails],
                                  loc_list: List[SecPreTransformLocationDetails]) -> Tuple[
        List[SecPreTransformPresentationArcDetails], List[SecPreTransformLocationDetails]]:
        """
        # a digit ending case has all labels ending with _<digits>, this case has to be handled especially, since
        # no hiearchy can be build. An example for this case is: 0000016160-21-000018
        # check for digit_ending
        example:
        <loc  label="Locator_us-gaap_StatementClassOfStockAxis_398"/>
        <presentationArc from="Locator_us-gaap_StatementClassOfStockAxis_403" to="Locator_us-gaap_ClassOfStockDomain_404" order="1.0" preferredLabel="terseLabel"/>
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
            label = label[:label.rfind('_')]
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
            to_label = to_label[:to_label.rfind('_')]
            new_preArc.to_entry = to_label

            from_label = preArc.from_entry
            from_label = from_label[:from_label.rfind('_')]
            new_preArc.from_entry = from_label

            new_preArc_list.append(new_preArc)

        return new_preArc_list, new_loc_list

    def _handle_ambiguous_child_parent_relation(self, preArc_list: List[SecPreTransformPresentationArcDetails]) -> List[
        SecPreTransformPresentationArcDetails]:
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

        for from_entry in from_list:
            count = sum(map(lambda x: x == from_entry, to_list))
            if count > 1:
                kick_out_list.append(from_entry)

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

        # now the entries can be removed from  orginial preArcList
        cleared_preArc_list: List[SecPreTransformPresentationArcDetails] = []

        for preArc in preArc_list:
            from_entry = preArc.from_entry
            if from_entry not in kick_out_list:
                cleared_preArc_list.append(preArc)

        return cleared_preArc_list

    def _find_root_node(self, preArc_list: List[SecPreTransformPresentationArcDetails]) -> str:
        """ finds the root node, expect only ONE entry. If there is more than one root node, then an exception is raised
            and this report will be skipped later in the process."""
        to_list: List[str] = []
        from_list: List[str] = []

        for preArc in preArc_list:
            to_list.append(preArc.to_entry)
            from_list.append(preArc.from_entry)

        root_nodes = list(set(from_list) - set(to_list))

        # there should be just one rootnote, at least in the presentations we are interested in
        if len(root_nodes) != 1:
            raise Exception("not exactly one root node")

        return root_nodes[0]

    def _eval_statement_canditate_helper(self, key: str, definition: List[EvalEntry]) -> int:
        key = key.lower()
        max_confidence = 0
        for key_def in definition:
            includes = key_def.includes
            excludes = key_def.excludes
            confidence = key_def.confidence

            if all(map_key in key for map_key in includes) and any(map_key in key for map_key in excludes) == False:
                max_confidence = max(max_confidence, confidence)

        return max_confidence

    def _eval_statement_canditate_label_helper(self, loc_list: List[SecPreTransformLocationDetails],
                                               definition: List[EvalEntry]):
        tag_list_lower = [loc_entry.tag.lower() for loc_entry in loc_list]

        max_confidence = 0
        for key_def in definition:
            includes = key_def.includes
            excludes = key_def.excludes
            confidence = key_def.confidence

            for tag in tag_list_lower:
                if all(map_key in tag for map_key in includes) and any(map_key in tag for map_key in excludes) == False:
                    max_confidence = max(max_confidence, confidence)

        kann man nicht so lösen. test müsste eher sein, falls es ein IS ist, könnte es aufgrund der labels auch ein CI sein?


        return max_confidence

    def _evaluate_statement_canditates(self, role: str, root_node: str,
                                       loc_list: List[SecPreTransformLocationDetails]) -> Dict[str, StmtConfidence]:
        # returns for matches stmt: {byrole: confidence, byroot:confidence, bylabel: confidence}

        result: Dict[str, StmtConfidence] = {}

        for key, definitions in self.stmt_eval_dict.items():
            role_keys_definition = definitions.role_keys
            root_keys_definition = definitions.root_keys
            label_definition = definitions.label_list

            details = StmtConfidence(
                byRole=self._eval_statement_canditate_helper(role, role_keys_definition),
                byRoot=self._eval_statement_canditate_helper(root_node, root_keys_definition),
                byLabel=self._eval_statement_canditate_label_helper(loc_list, label_definition)
            )

            if details.get_max_confidenc() > 0:
                result[key] = details

        return result

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

    def _calculate_line_nr(self, root_node: str, preArc_list: List[SecPreTransformPresentationArcDetails]):
        """ the 'only' thing this method does is to add the 'line' attribute to the preArc entries.
            this is done 'inplace'"""

        # building parent child relation from the from and to attributes of the preArc entries
        parent_child_dict: Dict[str, Dict[int, str]] = {}
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

    def _calculate_entries(self, root_node: str, loc_list: List[SecPreTransformLocationDetails],
                           preArc_list: List[SecPreTransformPresentationArcDetails]) -> List[PresentationEntry]:

        self._calculate_line_nr(root_node, preArc_list)

        # create dict by label for the loc-entries, so that we can link them to with the preArc entries
        loc_by_label_dict: Dict[str, SecPreTransformLocationDetails] = {}
        for loc in loc_list:
            label = loc.label
            loc_by_label_dict[label] = loc

        result: List[PresentationEntry] = []
        for preArc in preArc_list:
            # note: using [] instead of the get-method since we expect all keys to be present
            details = {}
            to_tag = preArc.to_entry

            loc_entry = loc_by_label_dict[to_tag]
            entry = PresentationEntry(
                version = loc_entry.version,
                tag = loc_entry.tag,
                plabel = preArc.preferredLabel,
                negating = preArc.negating,
                line = preArc.line)

            result.append(entry)

        return result

    def _check_for_role_name_to_ignore(self, role: str) -> bool:
        role_lower = role.lower()
        for ignore_keyword in self.role_report_ingore_keywords:
            if ignore_keyword in role_lower:
                return True
        return False

    def process_reports(self, adsh: str, data: Dict[int, SecPreTransformPresentationDetails]) -> \
            Tuple[Dict[int, PresentationReport], List[Tuple[str, str, str]]]:
        # processed the reports in the data.
        # organizes the reports by the report-type (BS, CP, CI, IS, CF, EQ) in the result

        # result is a dictionary with the chosen stmt as key and a list of the reports as Dicts
        result: Dict[int, PresentationReport] = {}
        error_collector: List[Tuple[str, str, str]] = []

        for idx, reportinfo in data.items():
            role: str = reportinfo.role
            inpth: int = int(reportinfo.inpth)
            loc_list: List[SecPreTransformLocationDetails] = reportinfo.loc_list
            preArc_list: List[SecPreTransformPresentationArcDetails] = reportinfo.preArc_list

            if (len(preArc_list) == 0) or (len(loc_list) == 0):  # no entries in node, so ignore
                continue

            # there are some strings which indicate that this is not a report we are interested in
            if self._check_for_role_name_to_ignore(role):
                continue

            try:
                preArc_list, loc_list = self._handle_digit_ending_case(preArc_list, loc_list)
                preArc_list = self._handle_ambiguous_child_parent_relation(preArc_list)
                root_node:str = self._find_root_node(preArc_list)

                stmt_canditates: Dict[str, StmtConfidence] = self._evaluate_statement_canditates(role, root_node,
                                                                                                 loc_list)
                if len(stmt_canditates) == 0:
                    continue

                self._calculate_key_tag_for_preArc(preArc_list)
                entries: List[PresentationEntry] = self._calculate_entries(root_node, loc_list, preArc_list)

                report = PresentationReport(
                    adsh = adsh, # str
                    role = role, # str
                    loc_list = loc_list, # List[SecPreTransformLocationDetails]
                    preArc_list = preArc_list, # List[SecPreTransformPresentationArcDetails]
                    rootNode = root_node, # str
                    entries = entries, # List[PresentationEntry]
                    inpth = inpth, # int
                    stmt_canditates = stmt_canditates # Dict[str, StmtConfidence]
                )
                result[idx] = report

            except Exception as err:
                error_collector.append((adsh, role, str(err)))
                # just log if the name gives a hint that this could be a primary statement
                role_candidates = self._evaluate_statement_canditates(role, "", [])
                if len(role_candidates) > 0:
                    logging.info(
                        "{} / {} skipped report with role {} : {}".format(adsh, list(role_candidates.keys()), role,
                                                                          str(err)))
                    print("{} / {} skipped report with role {} : {}".format(adsh, list(role_candidates.keys()), role,
                                                                            str(err)))
                continue

        return (result, error_collector)

    def _post_process_assign_report_to_stmt(self, report_data: Dict[int, PresentationReport]) -> \
            Dict[Tuple[str, int], List[PresentationReport]]:
        # based on the stmt_canditates info, this function figures out to which statement type the report belongs to. generally, there should be just one possiblity

        # the key is defined from the stmt type ('BS', 'IS', ..) the flog "inpth" which indicates wether it is  a "in parenthical" report
        result: Dict[Tuple[str, int], List[PresentationReport]] = {}

        # ensure that a report only belongs to one stmt type
        for idx, reportinfo in report_data.items():
            stmt_canditates_dict: Dict[str, StmtConfidence] = reportinfo.stmt_canditates
            stmt_canditates_keys = list(stmt_canditates_dict.keys())
            inpth = reportinfo.inpth

            stmt: str
            if len(stmt_canditates_keys) == 1:
                stmt = stmt_canditates_keys[0]
            else:
                # try to either find a single confidence of 2
                # or to find the entry with the biggest sum of confidence values

                conf_of_2_list = []
                max_sum_of_confidence = 0
                max_sum_of_confidence_stmt = None

                for stmt_key in stmt_canditates_keys:
                    confidence: StmtConfidence = stmt_canditates_dict[stmt_key]

                    if confidence.get_max_confidenc() == 2:
                        conf_of_2_list.append(stmt_key)

                    sum_of_confidence = confidence.get_confidence_sum()
                    if sum_of_confidence > max_sum_of_confidence:
                        max_sum_of_confidence = sum_of_confidence
                        max_sum_of_confidence_stmt = stmt_key

                if len(conf_of_2_list) == 1:
                    stmt = conf_of_2_list[0]
                else:
                    if len(conf_of_2_list) > 1:
                        logging.info(
                            "{} has confidence of 2 for several statement types {}".format(reportinfo.adsh,
                                                                                           conf_of_2_list))

                    stmt = max_sum_of_confidence_stmt

            if result.get((stmt, inpth)) == None:
                result[(stmt, inpth)] = []

            result[(stmt, inpth)].append(reportinfo)

        return result

    def _post_process_cp(self, stmt_list: List[PresentationReport]) -> List[PresentationReport]:
        # in all the reports, there was always just on CP entry
        # so we either return the first who was identified as CP by the rolename
        # or we return the first entry of the list (since CP is generally the first that appears in a report)
        for report_data in stmt_list:
            confidence_dict = report_data.stmt_canditates['CP']
            if confidence_dict.byRole == 2:
                return [report_data]
        first_entry = stmt_list[0]
        return [first_entry]

    def _post_process_bs(self, stmt_list: List[PresentationReport]) -> List[PresentationReport]:
        """
         often detail-reports contain the keywords in their role definition but also much more text.
         there are also cases with proper supparts of a company like 0001711269-21-000023

        """
        current_max_confidence = 0
        current_max_confidence_list:  List[PresentationReport] = []

        for report_data in stmt_list:
            confidence = report_data.stmt_canditates['BS']

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

    def process(self, adsh: str, data: Dict[int, SecPreTransformPresentationDetails]) -> \
            Tuple[List[PresentationEntry], List[Tuple[str, str, str]]]:

        results: List[PresentationEntry] = []

        report_data: Dict[int, PresentationReport]
        error_collector: List[Tuple[str, str, str]]

        report_data, error_collector = self.process_reports(adsh, data)

        stmt_data: Dict[Tuple[str, int], List[PresentationReport]] \
            = self._post_process_assign_report_to_stmt(report_data)

        reportnr = 0
        for stmtkey, stmt_list in stmt_data.items():
            stmt, inpth = stmtkey

            # todo: check if it is really necessary that a list is returned
            if stmt is 'CP':
                stmt_list = self._post_process_cp(stmt_list)

            if stmt is 'BS':
                stmt_list = self._post_process_bs(stmt_list)

            if stmt is 'CI':
                print("")

            for report in stmt_list:
                entries: List[PresentationEntry] = report.entries
                reportnr += 1
                for entry in entries:
                    entry.report = reportnr
                    entry.inpth = inpth
                    entry.stmt = stmt

                results.extend(entries)

        return (results, error_collector)
