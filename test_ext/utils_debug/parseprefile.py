from _02_xml.SecXmlPreParsing import SecPreXmlParser
from _00_common.DebugUtils import DataAccessByAdshTool

#special cases
# default namespace  xmlns="http://www.xbrl.org/2003/linkbase": d:/secprocessing/xml/2021-05-02/vgz-20210331_pre.xml

workdir = "d:/secprocessing/"

special_content_line_wrong = """<?xml version="1.0" encoding="UTF-8"?>
<link:linkbase xmlns:link="http://www.xbrl.org/2003/linkbase" xmlns:xbrldt="http://xbrl.org/2005/xbrldt" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.xbrl.org/2003/linkbase http://www.xbrl.org/2003/xbrl-linkbase-2003-12-31.xsd">
  <link:roleRef roleURI="http://www.huntsman.com/20201231/role/statement-consolidated-statements-of-comprehensive-income" xlink:href="hun-20201231.xsd#statement-consolidated-statements-of-comprehensive-income" xlink:type="simple"/>
  <link:presentationLink xlink:role="http://www.huntsman.com/20201231/role/statement-consolidated-statements-of-comprehensive-income" xlink:type="extended">
    <link:loc xlink:href="https://xbrl.sec.gov/dei/2019/dei-2019-01-31.xsd#dei_EntityDomain" xlink:label="dei_EntityDomain" xlink:type="locator"/>
    <link:loc xlink:href="https://xbrl.sec.gov/dei/2019/dei-2019-01-31.xsd#dei_LegalEntityAxis" xlink:label="dei_LegalEntityAxis" xlink:type="locator"/>
    <link:loc xlink:href="hun-20201231.xsd#hun_HuntsmanInternationalLLCMember" xlink:label="hun_HuntsmanInternationalLLCMember" xlink:type="locator"/>
    <link:loc xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_ComprehensiveIncomeNetOfTax" xlink:label="us-gaap_ComprehensiveIncomeNetOfTax-3" xlink:type="locator"/>
    <link:loc xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_ComprehensiveIncomeNetOfTaxAttributableToNoncontrollingInterest" xlink:label="us-gaap_ComprehensiveIncomeNetOfTaxAttributableToNoncontrollingInterest-n8" xlink:type="locator"/>
    <link:loc xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest" xlink:label="us-gaap_ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest-3" xlink:type="locator"/>
    <link:loc xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_OtherComprehensiveIncomeLossForeignCurrencyTransactionAndTranslationAdjustmentNetOfTax" xlink:label="us-gaap_OtherComprehensiveIncomeLossForeignCurrencyTransactionAndTranslationAdjustmentNetOfTax" xlink:type="locator"/>
    <link:loc xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_OtherComprehensiveIncomeLossNetOfTax" xlink:label="us-gaap_OtherComprehensiveIncomeLossNetOfTax-3" xlink:type="locator"/>
    <link:loc xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_OtherComprehensiveIncomeLossNetOfTaxPeriodIncreaseDecreaseAbstract" xlink:label="us-gaap_OtherComprehensiveIncomeLossNetOfTaxPeriodIncreaseDecreaseAbstract" xlink:type="locator"/>
    <link:loc xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_OtherComprehensiveIncomeLossPensionAndOtherPostretirementBenefitPlansAdjustmentNetOfTax" xlink:label="us-gaap_OtherComprehensiveIncomeLossPensionAndOtherPostretirementBenefitPlansAdjustmentNetOfTax-n8" xlink:type="locator"/>
    <link:loc xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_OtherComprehensiveIncomeOtherNetOfTax" xlink:label="us-gaap_OtherComprehensiveIncomeOtherNetOfTax" xlink:type="locator"/>
    <link:loc xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_ProfitLoss" xlink:label="us-gaap_ProfitLoss-1" xlink:type="locator"/>
    <link:loc xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementLineItems" xlink:label="us-gaap_StatementLineItems" xlink:type="locator"/>
    <link:loc xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementOfIncomeAndComprehensiveIncomeAbstract" xlink:label="us-gaap_StatementOfIncomeAndComprehensiveIncomeAbstract" xlink:type="locator"/>
    <link:loc xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementTable" xlink:label="us-gaap_StatementTable" xlink:type="locator"/>
    <link:presentationArc order="0" preferredLabel="http://www.xbrl.org/2003/role/label" xbrldt:closed="true" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="us-gaap_StatementOfIncomeAndComprehensiveIncomeAbstract" xlink:to="us-gaap_StatementTable" xlink:type="arc"/>
    <link:presentationArc order="0" preferredLabel="http://www.xbrl.org/2003/role/label" xbrldt:closed="true" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="dei_LegalEntityAxis" xlink:to="dei_EntityDomain" xlink:type="arc"/>
    <link:presentationArc order="0" preferredLabel="http://www.xbrl.org/2003/role/label" xbrldt:closed="true" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="us-gaap_StatementTable" xlink:to="dei_LegalEntityAxis" xlink:type="arc"/>
    <link:presentationArc order="1" preferredLabel="http://www.xbrl.org/2003/role/label" xbrldt:closed="true" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="dei_LegalEntityAxis" xlink:to="hun_HuntsmanInternationalLLCMember" xlink:type="arc"/>
    <link:presentationArc order="1" preferredLabel="http://www.xbrl.org/2003/role/label" xbrldt:closed="true" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="us-gaap_StatementTable" xlink:to="us-gaap_StatementLineItems" xlink:type="arc"/>
    <link:presentationArc order="0" preferredLabel="http://www.xbrl.org/2003/role/verboseLabel" xbrldt:closed="true" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="us-gaap_StatementLineItems" xlink:to="us-gaap_ProfitLoss-1" xlink:type="arc"/>
    <link:presentationArc order="1" preferredLabel="http://www.xbrl.org/2003/role/label" xbrldt:closed="true" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="us-gaap_StatementLineItems" xlink:to="us-gaap_OtherComprehensiveIncomeLossNetOfTaxPeriodIncreaseDecreaseAbstract" xlink:type="arc"/>
    <link:presentationArc order="0" preferredLabel="http://www.xbrl.org/2003/role/label" xbrldt:closed="true" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="us-gaap_OtherComprehensiveIncomeLossNetOfTaxPeriodIncreaseDecreaseAbstract" xlink:to="us-gaap_OtherComprehensiveIncomeLossForeignCurrencyTransactionAndTranslationAdjustmentNetOfTax" xlink:type="arc"/>
    <link:presentationArc order="1" preferredLabel="http://www.xbrl.org/2009/role/negatedLabel" xbrldt:closed="true" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="us-gaap_OtherComprehensiveIncomeLossNetOfTaxPeriodIncreaseDecreaseAbstract" xlink:to="us-gaap_OtherComprehensiveIncomeLossPensionAndOtherPostretirementBenefitPlansAdjustmentNetOfTax-n8" xlink:type="arc"/>
    <link:presentationArc order="2" preferredLabel="http://www.xbrl.org/2003/role/label" xbrldt:closed="true" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="us-gaap_OtherComprehensiveIncomeLossNetOfTaxPeriodIncreaseDecreaseAbstract" xlink:to="us-gaap_OtherComprehensiveIncomeOtherNetOfTax" xlink:type="arc"/>
    <link:presentationArc order="3" preferredLabel="http://www.xbrl.org/2003/role/totalLabel" xbrldt:closed="true" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="us-gaap_OtherComprehensiveIncomeLossNetOfTaxPeriodIncreaseDecreaseAbstract" xlink:to="us-gaap_OtherComprehensiveIncomeLossNetOfTax-3" xlink:type="arc"/>
    <link:presentationArc order="4" preferredLabel="http://www.xbrl.org/2003/role/totalLabel" xbrldt:closed="true" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="us-gaap_OtherComprehensiveIncomeLossNetOfTaxPeriodIncreaseDecreaseAbstract" xlink:to="us-gaap_ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest-3" xlink:type="arc"/>
    <link:presentationArc order="5" preferredLabel="http://www.xbrl.org/2009/role/negatedLabel" xbrldt:closed="true" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="us-gaap_OtherComprehensiveIncomeLossNetOfTaxPeriodIncreaseDecreaseAbstract" xlink:to="us-gaap_ComprehensiveIncomeNetOfTaxAttributableToNoncontrollingInterest-n8" xlink:type="arc"/>
    <link:presentationArc order="6" preferredLabel="http://www.xbrl.org/2003/role/totalLabel" xbrldt:closed="true" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="us-gaap_OtherComprehensiveIncomeLossNetOfTaxPeriodIncreaseDecreaseAbstract" xlink:to="us-gaap_ComprehensiveIncomeNetOfTax-3" xlink:type="arc"/>
    <link:presentationArc order="7" preferredLabel="http://www.xbrl.org/2003/role/verboseLabel" xbrldt:closed="true" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="us-gaap_OtherComprehensiveIncomeLossNetOfTaxPeriodIncreaseDecreaseAbstract" xlink:to="us-gaap_ProfitLoss-1" xlink:type="arc"/>
  </link:presentationLink>
</link:linkbase>
"""


def get_pre_xml_content_by_adsh(adsh: str)-> str :
    by_adsh = DataAccessByAdshTool(workdir, adsh, 2021, 1)
    return by_adsh.get_pre_xml_content()


def get_pre_xml_content_from_file(file: str)-> str:
    with open(file, "r", encoding="utf-8") as f:
        return  f.read()


def parse_content(adsh, content:  str):
    parser = SecPreXmlParser()
    df = parser.parse(adsh, content)
    df_clean = parser.clean_for_financial_statement_dataset(df, adsh)
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

    # interessanter Eintrag -> hat bei einem order ein ".02" 10440.02 und tatsächlich gibt es auch ein 1440.00 auf der selben Stufe
    # und das ist auch der dunstkreis, in welchem dann  die line bei einträgen nicht gesetzt ist..
    # es gibt Einträge ohne line und das is
    line_error_adsh = "0001564590-21-012671"
    line_error_adsh_2 = "0001437749-21-002772"

    content = special_content_line_wrong
    #content = get_pre_xml_content_by_adsh(line_error_adsh_2)

    parse_content("", content)

    print("")

# problem -> tag kann mehrmals vorkommen -> siehe missing_line_15_in_IS -> in IS kommt NetIncomeLoss mehrmals vor
# es muss zwischen key und tag/label unterschieden werden
# bei beispiel ist terse und total  unterschiedlich..
# d.h. aber, dass mehrere locs aufs selbe presentation_arc zeigen
# entsprechend muss beim iterieren aufgepasst werden.
# es gibt anscheined locs, die haben kein presentation.. -> evtl. sollten wir nur presentation_beachten.