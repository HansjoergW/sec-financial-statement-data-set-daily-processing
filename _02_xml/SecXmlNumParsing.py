from _02_xml.SecXmlParsingBase import SecXmlParserBase

import re
import calendar
import pandas as pd

from lxml import etree
from typing import Dict, List, Tuple, Optional


class SecNumXmlParser(SecXmlParserBase):
    """ Parses the data of an Num.Xml file and delivers the data in a similar format than the num.txt
       contained in the financial statements dataset of the sec."""

    # reports who's num file is part of the report use a "xbrli" prefix for all tags
    # reports for which the "num"xml has been created from the html don't use such a tag
    xbrli_prefix_regex = re.compile(r"xbrli:", re.IGNORECASE  + re.DOTALL)

    period_regex = re.compile(r"<period>|(</period>)", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    entity_regex = re.compile(r"<entity>|(</entity>)", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    identifier_regex = re.compile(r"(<identifier).*?(</identifier>)", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    # id_regex = re.compile(r"id=\"[^<]*?\"", re.IGNORECASE + re.MULTILINE + re.DOTALL)

    # single textblock tags like <xyTextBlock .. />
    # textblock_single_regex = re.compile(r"<[^/]*?TextBlock[^<]*?/>", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    # textblock with ending tag like <xyTextBlock...>...</xyTextBlock>
    # textblock_regex = re.compile(r"<[^/]*?TextBlock.*?<[/].*?TextBlock.*?>", re.IGNORECASE + re.MULTILINE + re.DOTALL)

    xbrlns_regex = re.compile(r"xmlns=\".*?\"", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    link_regex = re.compile(r"<link.*?>", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    link_end_regex = re.compile(r"</link.*?>", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    clean_tag_regex = re.compile(r"[{].*?[}]")
    # remove_wspace_regex = re.compile(r">[\s\r\n]*<", re.IGNORECASE + re.MULTILINE + re.DOTALL)
    remove_unicode_tag_regex = re.compile(r" encoding=\"utf-8\"", re.IGNORECASE + re.MULTILINE + re.DOTALL)

    find_year_regex = re.compile(r"\d\d\d\d")

    def __init__(self):
        super(SecNumXmlParser, self).__init__("num")
        pass

    def _strip_file(self, data: str) -> str:
        """removes unneeded content from the datastring, so that xml parsing will be faster"""
        data = self.xbrli_prefix_regex.sub("", data)
        data = self.identifier_regex.sub("", data)
        data = self.period_regex.sub("", data)
        data = self.entity_regex.sub("", data)


        data = self.xbrlns_regex.sub("", data) # clear xbrlns, so it is easier to parse

        data = self.link_regex.sub("", data)
        data = self.link_end_regex.sub("", data)
        # data = self.remove_wspace_regex.sub("><", data)
        data = self.remove_unicode_tag_regex.sub("", data)

        return data

    def _find_last_day_of_month(self, datastr:str) -> str:
        """finds the last day of the month in the datestring with format yyyy-mm-dd
        and returns it as yyyymmdd """
        yearstr  = datastr[0:4]
        monthstr = datastr[5:7]
        daystr = datastr[8:]

        year = int(yearstr)
        month = int(monthstr)

        last_day_of_month = calendar.monthrange(year, month)[1]
        return yearstr + monthstr + str(last_day_of_month).zfill(2)

    def _calculate_qtrs(self, year_start_s: str, month_start_s: str, year_end_s: str, month_end_s: str) -> int:
        """calculates the number of quartes between the start year/month and the end year/month"""
        year_start = int(year_start_s)
        year_end = int(year_end_s)
        month_start = int(month_start_s)
        month_end = int(month_end_s) + (year_end - year_start) * 12

        return int(round(float(month_end - month_start) / 3))

    def _read_contexts(self, root: etree._Element) -> Dict[str, Tuple[str,int,Optional[list]]]:
        contexts = list(root.iter('context'))
        context_map:  Dict[str, Tuple[str,int,Optional[list]]] = {}

        for context in contexts:
            instanttxt = None
            startdatetxt = None
            enddatetxt = None

            # generally, we are mainly interested in the contexts without a segment
            # however, the segment might be deliver interesting inside in future analysis
            segments = list(context.findall('.//*[@dimension]'))
            segments_list = []
            for segment in segments:
                segment_label = segment.text
                segment_dim = segment.get("dimension")
                segments_list.append(segment_dim + "/" + segment_label)

            if len(segments_list) == 0:
                segments_list = None

            id = context.get("id")
            instant = context.find('instant')
            if instant is not None:
                instanttxt = instant.text

            startdate = context.find('startDate')
            if startdate is not None:
                startdatetxt = startdate.text

            enddate = context.find('endDate')
            if enddate is not None:
                enddatetxt = enddate.text

            if instant is None:
                enddate = self._find_last_day_of_month(enddatetxt)
                qtrs = self._calculate_qtrs(startdatetxt[0:4], startdatetxt[5:7], enddatetxt[0:4], enddatetxt[5:7])

                context_map[id] = (enddate, qtrs, segments_list)
            else:
                enddate = self._find_last_day_of_month(instanttxt)
                context_map[id] = (enddate, 0, segments_list)

        return context_map

    def _find_company_namespaces(self, root: etree._Element) -> List[str]:
        official = ['xbrl.org', 'sec.gov','fasb.org','w3.org', 'xbrl.ifrs.org']
        company_namespaces = []
        for key, value in root.nsmap.items():
            if not any(x in value for x in official):
                company_namespaces.append(key)
        return company_namespaces

    def _read_tags(self, root: etree._Element) -> pd.DataFrame:
        company_namespaces = self._find_company_namespaces(root)

        us_gaap_ns = root.nsmap.get('us-gaap', None)
        ifrs_ns = root.nsmap.get('ifrs-full', None)

        versionyear = 0
        if us_gaap_ns:
            pos = us_gaap_ns.rfind("/") + 1
            versionyear = us_gaap_ns[pos:pos+4]

        if ifrs_ns:
            versionyear = self.find_year_regex.findall(ifrs_ns)[0]

        context_map = self._read_contexts(root)

        tags = list(root.findall('.//*[@unitRef]'))

        entries = []

        for tag in tags:
            temp_dict = {}

            value_text = tag.text
            decimals = tag.get("decimals")
            ctxtRef = tag.get("contextRef")
            unitRef = tag.get("unitRef").lower()
            tagname = self.clean_tag_regex.sub("", tag.tag)

            prefix = tag.prefix
            if prefix.startswith("ifrs"):
                prefix = "ifrs"

            if prefix in company_namespaces:
                version = 'company'
            else:
                version = prefix + "/" + str(versionyear)

            context_entry = context_map[ctxtRef]
            ddate = context_entry[0]
            qtrs = context_entry[1]
            segments = context_entry[2]

            if unitRef in ["usd","usdpershare","u_iso4217usd"]:
                unitRef = "USD"
            if unitRef == 'number':
                unitRef = 'pure'

            temp_dict['adsh']    = ''
            temp_dict['tag']     = tagname
            temp_dict['version'] = version
            temp_dict['coreg']   = ''
            temp_dict['ddate']   = ddate
            temp_dict['qtrs']    = qtrs
            temp_dict['uom']     = unitRef
            temp_dict['value']   = value_text
            temp_dict['footnote'] = ''
            temp_dict['segments'] = segments
            temp_dict['decimals'] = decimals

            entries.append(temp_dict)

        return pd.DataFrame(entries)

    def parse(self, data_in: str) -> pd.DataFrame:
        data = self._strip_file(data_in)
        data = bytes(bytearray(data, encoding='utf-8'))
        root = etree.fromstring(data)
        df = self._read_tags(root)
        return df

    def clean_for_financial_statement_dataset(self, df: pd.DataFrame, adsh: str = None) -> pd.DataFrame:
        df = (df[df.segments.isnull()]).copy()

        df['qtrs']  = df.qtrs.apply(int)
        df['value'] = pd.to_numeric(df['value'], errors='coerce')

        # die 'values' in den txt files haben maximal 4 nachkommastellen...
        df['value'] = df.value.round(4)

        df['adsh'] = adsh
        df.loc[df.version == 'company', 'version'] = adsh

        df.drop(['segments'], axis=1, inplace=True)
        df.drop_duplicates(inplace=True)

        # set the indexes
        df.set_index(['adsh', 'tag','version','ddate','qtrs'], inplace=True)

        # and sort by the precision
        # it can happen that the same tag is represented in the reports multiple times with different precision
        # and it looks as if the "txt" data of the sec is then produced with the lower precision
        df.sort_values('decimals', inplace=True)
        df_double_index_mask = df.index.duplicated(keep='first')

        df = df[~df_double_index_mask]

        return df