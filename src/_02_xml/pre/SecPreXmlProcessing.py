from typing import Dict, Union, List, Tuple, Set
import logging
import pprint as pp


class SecPreXmlDataProcessor():
    """
    processes the extracted and transformed data from a prexml file
    """

    # keywords that indicate the type of the report
    stmt_keyword_map: List[Tuple[List[str], str]] = [
        (['consolidated', 'statement', 'income', 'comprehensive'], 'CI'),
        (['consolidated', 'statement', 'income'], 'IS'),
        (['consolidated', 'statement', 'operation'], 'IS'),
        (['incomestatementabstract'], 'IS'),
        (['consolidated', 'statement', 'financialposition'], 'BS'),
        (['consolidated', 'statement', 'cashflow'], 'CF'),
        (['statement', 'shareholder', 'equity'], 'EQ'),
        (['statement', 'stockholder', 'equity'], 'EQ'),
        (['statement', 'shareowner', 'equity'], 'EQ'),
        (['statement', 'stockowner', 'equity'], 'EQ'),
        (['document', 'entity', 'information'], 'CP'),
        (['balancesheet'], 'BS'),
        (['cover'], 'CP'),
    ]

    key_tag_separator = '$$$'

    def __init__(self):
        pass

    def _handle_digit_ending_case(self, preArc_list: List[Dict[str, str]], loc_list: List[Dict[str, str]]) -> Tuple[
        List[Dict[str, str]], List[Dict[str, str]]]:
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
            digit_ending = digit_ending and loc.get('digit_ending')

        # no digit_ending case, return list without processing
        if not digit_ending:
            return preArc_list, loc_list

        # a digit ending case is disjoint between from and to list
        to_list: List[str] = []
        from_list: List[str] = []

        for preArc in preArc_list:
            to_list.append(preArc.get('to'))
            from_list.append(preArc.get('from'))

        # if not disjoint, return preArc and loc lsit without processing
        if not set(to_list).isdisjoint(set(from_list)):
            return preArc_list, loc_list

        # this is a digit ending case:
        # therefore the _<digit> part has to be removed from the label
        # furthermore, every lable may appear only once in the loclist

        new_loc_list: List[Dict[str, str]] = []
        new_loc_label_list: List[str] = []

        for loc in loc_list:
            new_loc = loc.copy()
            label = loc.get('label')
            label = label[:label.rfind('_')]
            new_loc['label'] = label

            if label in new_loc_label_list:
                continue
            new_loc_list.append(new_loc)
            new_loc_label_list.append(label)

        # in the preArc, the _<digit> part has to be removed from the from and to entries
        new_preArc_list: List[Dict[str, str]] = []
        for preArc in preArc_list:
            new_preArc = preArc.copy()
            to_label = preArc.get('to')
            to_label = to_label[:to_label.rfind('_')]
            new_preArc['to'] = to_label

            from_label = preArc.get('from')
            from_label = from_label[:from_label.rfind('_')]
            new_preArc['from'] = from_label

            new_preArc_list.append(new_preArc)

        return new_preArc_list, new_loc_list

    def _handle_ambiguous_child_parent_relation(self, preArc_list: List[Dict[str, str]]) -> List[Dict[str, str]]:
        # there are some rare cases (2 in 5500 reports from 2021-q1) when for a single node no line can be evaluated.
        # this is the reason when the child-parent relation is ambiguous.
        # e.g. "0001562762-21-000101" # StatementConsolidatedStatementsOfStockholdersEquity because there
        # in these cases, we have to kick out that entry and its children

        # these cases are identified, when a from node appears more than once in a two node
        to_list: List[str] = []
        from_list: List[str] = []

        for preArc in preArc_list:
            to_list.append(preArc.get('to'))
            from_list.append(preArc.get('from'))

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
                to_entry = preArc.get('to')
                from_entry = preArc.get('from')
                if from_entry in kick_out_list:
                    if to_entry not in kick_out_list:
                        kick_out_list.append(to_entry)
                        new_entries_found = True


        # now the entries can be removed from  orginial preArcList
        cleared_preArc_list: List[Dict[str, str]] = []

        for preArc in preArc_list:
            from_entry = preArc.get('from')
            if from_entry not in kick_out_list:
                cleared_preArc_list.append(preArc)

        return cleared_preArc_list

    def _find_root_node(self, preArc_list: List[Dict[str, str]]) -> str:
        """ finds the root node, expect only ONE entry. If there is more than one root node, then an exception is raised
            and this report will be skipped later in the process."""
        to_list: List[str] = []
        from_list: List[str] = []

        for preArc in preArc_list:
            to_list.append(preArc.get('to'))
            from_list.append(preArc.get('from'))

        root_nodes = list(set(from_list) - set(to_list))

        # there should be just one rootnote, at least in the presentations we are interested in
        if len(root_nodes) != 1:
            raise Exception("not exactly one root node")

        return root_nodes[0]

    def _evaluate_statement(self, role: str, root_node: str, loc_list: List[Dict[str, str]]) -> Union[str, None]:
        """ tries to figure out the """

        role_and_root_node: List[str] = [role.lower(), root_node.lower()]

        for map_entry in self.stmt_keyword_map:
            map_stmt: str = map_entry[1]
            map_keys: List[str] = map_entry[0]

            for entry in role_and_root_node:
                if all(map_key in entry for map_key in map_keys):
                    return map_stmt

        return None

    def _calculate_key_tag_for_preArc(self, preArc_list: List[Dict[str, str]]):
        # the key_tag is needed in order to calculate the correct line number. it is necessary, since
        # it is possible that the same to_tag appears twice under different from_tags or (!) also the same from_tag.
        # but this seems to be only the case, if the to_tag is not also a from_tag.
        # therefore the keytag is the "to_tag" for the entries which have children (so they also appear in the from tag)
        # for the entries which don't have children, the keytag is the combination of from_tag, to_tag and order

        to_list: List[str] = []
        from_list: List[str] = []

        for preArc in preArc_list:
            to_list.append(preArc.get('to'))
            from_list.append(preArc.get('from'))


        for preArc in preArc_list:
            to_tag = preArc.get('to')
            from_tag = preArc.get('from')
            order_str = str(preArc.get('order_nr'))

            if to_tag in from_list:
                key_tag = to_tag
            else:
                key_tag = to_tag + self.key_tag_separator + from_tag + self.key_tag_separator + order_str

            preArc['key_tag'] = key_tag

    def _calculate_line_nr(self, root_node: str, preArc_list: List[Dict[str, str]]):
        """ the 'only' thing this method does is to add the 'line' attribute to the preArc entries.
            this is done 'inplace'"""

        # building parent child relation from the from and to attributes of the preArc entries
        parent_child_dict: Dict[str, Dict[int, str]] = {}
        preArc_by_keytag_dict: Dict[str, Dict[str, str]] = {}
        for preArc in preArc_list:
            order_nr = preArc['order_nr']
            key_tag = preArc['key_tag']
            from_tag = preArc['from']

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

            preArc_by_keytag_dict[child]['line'] = line

            grand_children = parent_child_ordered_list.get(child)
            if grand_children is not None:
                node_path.append(child)
                node_index[child] = 0

            line += 1

    def _calculate_entries(self, root_node: str, loc_list: List[Dict[str, str]], preArc_list: List[Dict[str, str]]) -> \
            List[Dict[str, str]]:

        self._calculate_line_nr(root_node, preArc_list)

        # create dict by label for the loc-entries, so that we can link them to with the preArc entries
        loc_by_label_dict: Dict[str, Dict[str]] = {}
        for loc in loc_list:
            label = loc['label']
            loc_by_label_dict[label] = loc

        result: List[Dict[str, str]] = []
        for preArc in preArc_list:
            # note: using [] instead of the get-method since we expect all keys to be present
            details = {}
            to_tag = preArc['to']

            loc_entry = loc_by_label_dict[to_tag]
            details['version'] = loc_entry['version']
            details['tag'] = loc_entry['tag']

            details['plabel'] = preArc['preferredLabel']
            details['negating'] = preArc['negating']

            details['line'] = preArc['line']

            result.append(details)

        return result

    def process(self, adsh: str, data: Dict[int, Dict[str, Union[str, List[Dict[str, str]]]]]) -> List[
        Dict[str, Union[str, int]]]:

        reportnr = 0
        results: List[Dict[str, Union[str, int]]] = []
        for idx, reportinfo in data.items():
            role: str = reportinfo.get('role')
            inpth: int = int(reportinfo.get('inpth'))
            loc_list: List[Dict[str, str]] = reportinfo.get('loc_list')
            preArc_list: List[Dict[str, str]] = reportinfo.get('preArc_list')

            try:
                preArc_list, loc_list = self._handle_digit_ending_case(preArc_list, loc_list)
                preArc_list = self._handle_ambiguous_child_parent_relation(preArc_list)

                root_node = self._find_root_node(preArc_list)
                stmt = self._evaluate_statement(role, root_node, loc_list)
                if stmt is None:
                    continue

                self._calculate_key_tag_for_preArc(preArc_list)
                entries = self._calculate_entries(root_node, loc_list, preArc_list)
                reportnr += 1
                for entry in entries:
                    entry['report'] = reportnr
                    entry['stmt'] = stmt
                    entry['inpth'] = inpth

                results.extend(entries)

            except Exception as err:
                # often a report contains a "presentation" entry with  more than one root node.
                # so far, we do not handle this, since that type of problem is mainly in presentations which do
                # not belong to the primary fincancial statements. so we ignore it

                # just log if the name gives a hint that this could be a primary statement
                if self._evaluate_statement(role, "", []) is not None:
                    logging.info("{} skipped report with role {} : {}".format(adsh, role, str(err)))
                    print("{} skipped report with role {} : {}".format(adsh, role, str(err)))
                continue

        return results
