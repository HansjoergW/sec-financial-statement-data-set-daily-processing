from typing import List, Dict, Tuple

""" transforms the raw content of the information inside the xml in the a usable form. does not any processing of the data"""


class SecPreXmlTransformer():

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
            version = 'company'

        pos = complete_tag.find('_')
        tag = complete_tag[pos+1:]

        details['tag'] = tag
        details['version'] = version
        return details



    def transform(self, data: Dict[int,Tuple[str, List[Dict[str,str]], List[Dict[str, str]]]]) -> Dict[int,Tuple[str, List[Dict[str,str]], List[Dict[str, str]]]]:
        pass

# evtl. noch herausfinden, ob es spezieller labeltyp ist, mit _12 oder so ending
# label anpassen könnte man dann direkt hier machen
# prüfen, ob nach letztem _ nur digits vorhanden sind

# in loc: tag und version aus href berechnen
#

# in arc:
# order -> wandeln: order_nr = int(float(arc.get('order')))
# add negating:    negated = False
#                  if prefered_label:
#                     negated = "negated" in prefered_label
# key tag bestimmen             if to_tag in from_list:
                    #                 key_tag = to_tag
                    #             else:
                    #                 key_tag = to_tag + "$$$" + prefered_label
#
