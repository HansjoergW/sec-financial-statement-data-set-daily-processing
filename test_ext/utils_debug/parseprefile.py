from _02_xml.SecXmlPreParsing import SecPreXmlParser
from _00_common.DebugUtils import DataAccessByAdshTool

#special cases
# default namespace  xmlns="http://www.xbrl.org/2003/linkbase": d:/secprocessing/xml/2021-05-02/vgz-20210331_pre.xml

workdir = "d:/secprocessing/"


def get_pre_xml_content_by_adsh(adsh: str)-> str :
    by_adsh = DataAccessByAdshTool(workdir, adsh, 2021, 1)
    return by_adsh.get_pre_xml_content()


def get_pre_xml_content_from_file(file: str)-> str:
    with open(file, "r", encoding="utf-8") as f:
        return  f.read()


def parse_content(content:  str):
    parser = SecPreXmlParser()
    df = parser.parse(content)
    df_clean = parser.clean_for_financial_statement_dataset(df, "accnr")
    print(df_clean.shape) # die meisten attribute sind im index, daher ist die anzahl der spalten nur 3


if __name__ == '__main__':

    file_ok = "d:/secprocessing/xml/2021-04-24/blpg-20200630_pre.xml"
    file_nok = "d:/secprocessing/xml/2021-05-02/vgz-20210331_pre.xml"
    file_empty= "d:/secprocessing/xml/2021-05-06/nvec-20210331_pre.xml"
    file_oder = "d:/secprocessing/xml/2021-04-24/uboh-20201231_pre.xml"
    order_problem = "d:/secprocessing/xml/2021-04-24/temir-20200831_pre.xml"
    key_problem = "d:/secprocessing/xml/2021-04-24/gbt-20201231_pre.xml"
    more_than_one_root_node_problem = "d:/secprocessing/xml/2021-04-24/npk-20201231_pre.xml"
    more_than_one_root_node_problem_2 = "d:/secprocessing/xml/2021-04-24/dov-20210331_pre.xml"
    no_attr_stmt = "d:/secprocessing/xml/2021-04-24/pssr-20210131_pre.xml"
    missing_cover_page = "d:/secprocessing/xml/2021-04-24/ll-20201231_pre.xml"
    missing_line_15_in_IS = 'd:/secprocessing/xml/2021-04-24/nktx-20201231_pre.xml'
    # content = get_pre_xml_content_from_file(missing_line_15_in_IS)

    missing_statements_adsh = "0000019584-21-000003" # not every pres-arc has preferredLabel attribut
    missing_statements_2_adsh = "0000004904-21-000010" # loc labels with '.' in the name
    missing_statements_3_adsh = "0000026172-21-000012" # root node in uppercase für CP
    missing_statements_4_adsh = "0000021344-21-000008" # CI not found -> root name anders
    missing_statements_5_adsh = "0000031791-21-000003" # CI not found -> kein root node mit entsprechendem Hinweis
    missing_statements_6_adsh = "0000018255-21-000004" # diverse not found
    missing_statements_7_adsh = "0000002969-21-000012" # CI (2x) not present
    missing_statements_8_adsh = "0000016918-21-000010" # IS not present
    missing_statements_9_adsh = "0000024090-21-000012" # IS not present
    missing_statements_10_adsh = "0000034903-21-000020" # IS not present

    un_not_present_1_adsh = "0000003570-21-000039" # identified as CF
    no_data_1_adsh = "0000016160-21-000018" # numbered labels
    no_matching_report_1 = "0000018926-21-000017" # almost all none matching
    no_matching_report_2 = "0000031791-21-000003" # no matching EQ and BS
    no_matching_report_3 = "0000028412-21-000054" # no matching EQ
    no_matching_report_4 = "0000016918-21-000010" # no matching CF
    two_canditates_1 = "0000014272-21-000066"

    content = get_pre_xml_content_by_adsh(two_canditates_1)

    parse_content(content)
    print("")

# problem -> tag kann mehrmals vorkommen -> siehe missing_line_15_in_IS -> in IS kommt NetIncomeLoss mehrmals vor
# es muss zwischen key und tag/label unterschieden werden
# bei beispiel ist terse und total  unterschiedlich..
# d.h. aber, dass mehrere locs aufs selbe presentation_arc zeigen
# entsprechend muss beim iterieren aufgepasst werden.
# es gibt anscheined locs, die haben kein presentation.. -> evtl. sollten wir nur presentation_beachten.