from _02_xml.SecXmlPreParsing import SecPreXmlParser
from _00_common.DebugUtils import DataAccessByAdshTool

"""
Helper Class to process a single report based on the ADSH Nummer or directly from an xml content 
"""


workdir = "d:/secprocessing/"

xml_content = """
"""


def get_pre_xml_content_by_adsh(adsh: str)-> str :
    by_adsh = DataAccessByAdshTool(workdir, adsh, 2021, 1)
    return by_adsh.get_pre_xml_content()


def get_pre_xml_content_from_file(file: str)-> str:
    with open(file, "r", encoding="utf-8") as f:
        return  f.read()


def parse_content(adsh, content:  str):
    parser = SecPreXmlParser()
    (df, errors) = parser.parse(adsh, content)
    df_clean = parser.clean_for_financial_statement_dataset(df, adsh)
    print(df_clean.shape) # die meisten attribute sind im index, daher ist die anzahl der spalten nur 3


if __name__ == '__main__':
    # adsh = "0001010412-21-000004"
    # adsh = "0001079973-21-000172"
    # adsh = "0001091818-21-000034"
    # adsh = "0001140361-21-008496"
    # adsh = "0001174947-21-000152"
    # adsh = "0001174947-21-000157"
    # adsh = "0001174947-21-000168"
    # adsh = "0001174947-21-000315"
    # adsh = "0001178913-21-000696"
    #adsh = "0001213900-21-019217" # missing CI
    adsh = "0000076605-21-000059" # missing BS


    content = get_pre_xml_content_by_adsh(adsh)
    #content = xml_content
    parse_content(adsh, content)


# old special cases

"""
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

    # interessanter Eintrag -> hat bei einem order ein ".02" 10440.02 und tatsächlich gibt es auch ein 1440.00 auf der selben Stufe
    # und das ist auch der dunstkreis, in welchem dann  die line bei einträgen nicht gesetzt ist..
    # es gibt Einträge ohne line und das is
    line_error_adsh = "0001564590-21-012671"
    line_error_adsh_2 = "0001437749-21-002772"
    line_error_adsh_3 = "0000018255-21-000004"
    line_error_adsh_4 = "0001562762-21-000101" # StatementConsolidatedStatementsOfStockholdersEquity
    line_error_adsh_5 = "0001564590-21-012964" # StatementConsolidatedStatementsOfCashFlows

    multiple_root_nodes_1 = "0000066756-21-000025" # several statements ending with role-name _1
    not_one_root_node_1 = "0000072903-21-000012"
    not_one_root_node_2 = "0000829224-21-000029" #
    not_one_root_node_3 = "0000920371-21-000042" #
    not_one_root_node_4 = "0001254699-21-000005" #

    no_cp_report_1 = "0001558370-21-003462" # '0000916365-21-000052', '0001702744-21-000011', '0000773141-21-000024'
    many_cp_reports_1 = "0001829126-21-002055" # 0000089089-21-000012, 0000898174-21-000006, 0001829126-21-002055
    many_bs_reports_1 = "0001193125-21-094619"
    no_bs_inpth_report_in_zip =     '0000007789-21-000018'

    # 3: 0001711269-21-000023 / 2: 0000074208-21-000025, 0000354707-21-000036, 0000701869-21-000011, 0000826675-21-000015, 0000933036-21-000049, 0001010412-21-000004, 0001025996-21-000062
    # more_than_one_bs = "0000826675-21-000015"
    #missing_bs = "0001553350-21-000261" #    0001387131-21-002995 0001387131-21-002996


    # 0000012208-21-000012: andere root node in parentheticals

    # 0001213900-21-019311 BS: sieht aus als wäre das als CashFlow betitelt!
    # '0001193125-21-102032', '0001669374-21-000016' '0001539816-21-000003' '0001775098-21-000005' '0001587650-21-000010' # ->  kein normaler Report
    
"""

