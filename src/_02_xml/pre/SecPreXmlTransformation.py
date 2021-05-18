from typing import List, Dict, Union
import re

""" transforms the raw content of the information inside the xml in the a usable form. does not do any processing of the data, 
but adds additional information"""


class SecPreXmlTransformer():

    digit_ending_label_regex = re.compile(r"_\d*$")

    def __init__(self):
        pass

    @staticmethod
    def _get_version_tag_name_from_href(href: str) -> Dict[str, str]:
        # Attention: extend testcases if adaptions should be necessary.

        # in the href-definition, the first part indicates wich namespace and version it, if they start with http:
        # eg: xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_AccountingStandardsUpdate201802Member"
        # if it is a company namespace, then there is no http:
        # eg: xlink:href="pki-20210103.xsd#pki_AccountingStandardsUpdate_201616Member"
        # if it is a "company", then the version of the tag is the adsh number of the report
        # otherwise, the year and namespace is extracted from the namespace path.
        # the used "tag" itself follows after the hash, without the content before the first "_"
        # eg: us-gaap_AccountingStandardsUpdate201802Member -> AccountingStandardsUpdate201802Member
        # eg: pki_AccountingStandardsUpdate_201616Member    -> AccountingStandardsUpdate_201616Member
        # Note
        # tags kann have '_' in their name

        details: Dict[str, str] = {}
        href_parts = href.split('#')
        complete_tag = href_parts[1]
        version = None
        if href_parts[0].startswith('http'):
            ns_parts = href_parts[0].split('/')
            version = ns_parts[3] + '/' + ns_parts[4]
        else:
            version = 'company' # special hint to indicate that this is a company specifig tag

        pos = complete_tag.find('_')
        tag = complete_tag[pos + 1:]

        details['tag'] = tag
        details['version'] = version
        return details

    def transform_loc(self, loc_list: List[Dict[str, str]]):
        for loc in loc_list:
            tag_version: Dict[str, str] = SecPreXmlTransformer._get_version_tag_name_from_href(loc.get('href'))
            loc['version'] = tag_version['version']
            loc['tag'] = tag_version['tag']

            # there are some special cases of reports which adds a running number to every appereance of a label,
            # also in the to and from attributes of the preArc entries (e.g. 0000016160-21-000018).
            # (like '...._12'). This makes it impossible to build up the hierarchy and therefore to find the root.
            # therefore, this labels have to handled in a special way
            loc['digit_ending'] = False
            if self.digit_ending_label_regex.search(loc.get('label')):
                loc['digit_ending'] = True

    def transform_preArc(self, preArc_list: List[Dict[str, str]]):
        for preArc in preArc_list:

            # figure out wether the preferredLabel gives a  hint that the displayed number is inverted
            negated = "negated" in preArc['preferredLabel']
            preArc['negating'] = negated

            # some xmls use 0.0, 1.0 ... as order number instead of a pure int, so we ensure that we have an order_nr that is always an int
            preArc['order_nr'] = int(float(preArc.get('order')))

    def transform(self, data: Dict[int, Dict[str, Union[str, List[Dict[str, str]]]]]) -> Dict[int, Dict[str, Union[str, List[Dict[str, str]]]]]:
        for k,v in data.items():
            self.transform_loc(v.get('loc_list'))
            self.transform_preArc(v.get('preArc_list'))

            # figure out if data in a report where contained in parantheses
            v['inpth'] = 0
            if "parenthetical" in v.get('role'):
                v['inpth'] = 1

        return data