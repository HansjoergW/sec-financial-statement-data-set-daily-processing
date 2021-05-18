from typing import Dict, Union, List, Tuple, Set

class SecPreXmlDataProcessor():
    """
    processes the extracted and transformed data from a prexml file
    """
    def __init__(self):
        pass

    def _handle_digit_ending_case(self, preArc_list: List[Dict[str, str]], loc_list: List[Dict[str, str]]) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
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
        if not  digit_ending:
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

    def _find_root_node(self, preArc_list: List[Dict[str, str]]) -> str:
        """ finds the root node, expect only ONE entry. If there is more than one root node, then an exception is raised
            and this report will be skipped later in the process."""
        to_list: List[str] = []
        from_list: List[str] = []

        for preArc in preArc_list:
            to_list.append(preArc.get('to'))
            from_list.append(preArc.get('from'))

        root_nodes = set(from_list) - set(to_list)

        # there should be just one rootnote, at least in the presentations we are interested in
        if len(root_nodes) != 1:
            raise Exception("not exactly one root node")

        return root_nodes[0]

    def process(self, data: Dict[int, Dict[str, Union[str, List[Dict[str, str]]]]]) -> List[Dict[str, str]]:

        for reportnr, reportinfo in data.items():
            role: str = data.get('role')
            loc_list: List[Dict[str, str]] = reportinfo.get('loc_list')
            preArc_list: List[Dict[str, str]] = reportinfo.get('preArc_list')

            preArc_list, loc_list = self._handle_digit_ending_case(preArc_list, loc_list)

            root_node = self._find_root_node(preArc_list)

        return None