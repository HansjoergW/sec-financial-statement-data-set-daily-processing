from _02_xml.SecXmlPreParsing import SecPreXmlParser
from _00_common.DebugUtils import DataAccessByAdshTool

#special cases
# default namespace  xmlns="http://www.xbrl.org/2003/linkbase": d:/secprocessing/xml/2021-05-02/vgz-20210331_pre.xml

workdir = "d:/secprocessing/"

special_content_line_wrong = """<?xml version="1.0" encoding="UTF-8"?>
<linkbase xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.xbrl.org/2003/instance http://www.xbrl.org/2003/xbrl-instance-2003-12-31.xsd" xmlns="http://www.xbrl.org/2003/linkbase" xmlns:xbrli="http://www.xbrl.org/2003/instance" xmlns:xlink="http://www.w3.org/1999/xlink">
    <presentationLink xlink:type="extended" xlink:role="http://www.marlinleasing.com/role/StatementConsolidatedStatementsOfStockholdersEquity">
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementTable" xlink:label="Locator_us-gaap_StatementTable_703" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementEquityComponentsAxis" xlink:label="Locator_us-gaap_StatementEquityComponentsAxis_704" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_StatementTable_703" xlink:to="Locator_us-gaap_StatementEquityComponentsAxis_704" order="1.0" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementEquityComponentsAxis" xlink:label="Locator_us-gaap_StatementEquityComponentsAxis_725" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_EquityComponentDomain" xlink:label="Locator_us-gaap_EquityComponentDomain_726" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_StatementEquityComponentsAxis_725" xlink:to="Locator_us-gaap_EquityComponentDomain_726" order="1.0" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_EquityComponentDomain" xlink:label="Locator_us-gaap_EquityComponentDomain_727" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_CommonStockMember" xlink:label="Locator_us-gaap_CommonStockMember_728" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_EquityComponentDomain_727" xlink:to="Locator_us-gaap_CommonStockMember_728" order="1.0" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_EquityComponentDomain" xlink:label="Locator_us-gaap_EquityComponentDomain_729" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_AdditionalPaidInCapitalMember" xlink:label="Locator_us-gaap_AdditionalPaidInCapitalMember_730" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_EquityComponentDomain_729" xlink:to="Locator_us-gaap_AdditionalPaidInCapitalMember_730" order="2.0" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_EquityComponentDomain" xlink:label="Locator_us-gaap_EquityComponentDomain_731" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_AccumulatedOtherComprehensiveIncomeMember" xlink:label="Locator_us-gaap_AccumulatedOtherComprehensiveIncomeMember_732" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_EquityComponentDomain_731" xlink:to="Locator_us-gaap_AccumulatedOtherComprehensiveIncomeMember_732" order="3.0" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_EquityComponentDomain" xlink:label="Locator_us-gaap_EquityComponentDomain_733" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_RetainedEarningsMember" xlink:label="Locator_us-gaap_RetainedEarningsMember_734" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_EquityComponentDomain_733" xlink:to="Locator_us-gaap_RetainedEarningsMember_734" order="4.0" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementTable" xlink:label="Locator_us-gaap_StatementTable_705" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/srt/2020/elts/srt-2020-01-31.xsd#srt_RestatementAxis" xlink:label="Locator_srt_RestatementAxis_706" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_StatementTable_705" xlink:to="Locator_srt_RestatementAxis_706" order="2.0" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/srt/2020/elts/srt-2020-01-31.xsd#srt_RestatementAxis" xlink:label="Locator_srt_RestatementAxis_715" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/srt/2020/elts/srt-2020-01-31.xsd#srt_RestatementDomain" xlink:label="Locator_srt_RestatementDomain_716" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_srt_RestatementAxis_715" xlink:to="Locator_srt_RestatementDomain_716" order="1.0" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/srt/2020/elts/srt-2020-01-31.xsd#srt_RestatementDomain" xlink:label="Locator_srt_RestatementDomain_717" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/srt/2020/elts/srt-2020-01-31.xsd#srt_RevisionOfPriorPeriodAccountingStandardsUpdateAdjustmentMember" xlink:label="Locator_srt_RevisionOfPriorPeriodAccountingStandardsUpdateAdjustmentMember_718" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_srt_RestatementDomain_717" xlink:to="Locator_srt_RevisionOfPriorPeriodAccountingStandardsUpdateAdjustmentMember_718" order="1.0" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementTable" xlink:label="Locator_us-gaap_StatementTable_707" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/srt/2020/elts/srt-2020-01-31.xsd#srt_CumulativeEffectPeriodOfAdoptionAxis" xlink:label="Locator_srt_CumulativeEffectPeriodOfAdoptionAxis_708" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_StatementTable_707" xlink:to="Locator_srt_CumulativeEffectPeriodOfAdoptionAxis_708" order="3.0" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/srt/2020/elts/srt-2020-01-31.xsd#srt_CumulativeEffectPeriodOfAdoptionAxis" xlink:label="Locator_srt_CumulativeEffectPeriodOfAdoptionAxis_721" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/srt/2020/elts/srt-2020-01-31.xsd#srt_CumulativeEffectPeriodOfAdoptionDomain" xlink:label="Locator_srt_CumulativeEffectPeriodOfAdoptionDomain_722" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_srt_CumulativeEffectPeriodOfAdoptionAxis_721" xlink:to="Locator_srt_CumulativeEffectPeriodOfAdoptionDomain_722" order="1.0" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/srt/2020/elts/srt-2020-01-31.xsd#srt_CumulativeEffectPeriodOfAdoptionDomain" xlink:label="Locator_srt_CumulativeEffectPeriodOfAdoptionDomain_723" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/srt/2020/elts/srt-2020-01-31.xsd#srt_CumulativeEffectPeriodOfAdoptionAdjustmentMember" xlink:label="Locator_srt_CumulativeEffectPeriodOfAdoptionAdjustmentMember_724" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_srt_CumulativeEffectPeriodOfAdoptionDomain_723" xlink:to="Locator_srt_CumulativeEffectPeriodOfAdoptionAdjustmentMember_724" order="1.0" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementTable" xlink:label="Locator_us-gaap_StatementTable_701" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementLineItems" xlink:label="Locator_us-gaap_StatementLineItems_702" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_StatementTable_701" xlink:to="Locator_us-gaap_StatementLineItems_702" order="5.0" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementLineItems" xlink:label="Locator_us-gaap_StatementLineItems_581" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StockIssuedDuringPeriodValueNewIssues" xlink:label="Locator_us-gaap_StockIssuedDuringPeriodValueNewIssues_582" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_StatementLineItems_581" xlink:to="Locator_us-gaap_StockIssuedDuringPeriodValueNewIssues_582" order="3.0" preferredLabel="http://www.xbrl.org/2003/role/verboseLabel" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementLineItems" xlink:label="Locator_us-gaap_StatementLineItems_583" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StockIssuedDuringPeriodSharesNewIssues" xlink:label="Locator_us-gaap_StockIssuedDuringPeriodSharesNewIssues_584" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_StatementLineItems_583" xlink:to="Locator_us-gaap_StockIssuedDuringPeriodSharesNewIssues_584" order="4.0" preferredLabel="http://www.xbrl.org/2003/role/verboseLabel" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementLineItems" xlink:label="Locator_us-gaap_StatementLineItems_585" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StockRepurchasedDuringPeriodValue" xlink:label="Locator_us-gaap_StockRepurchasedDuringPeriodValue_586" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_StatementLineItems_585" xlink:to="Locator_us-gaap_StockRepurchasedDuringPeriodValue_586" order="5.0" preferredLabel="http://www.xbrl.org/2009/role/negatedLabel" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementLineItems" xlink:label="Locator_us-gaap_StatementLineItems_587" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StockRepurchasedDuringPeriodShares" xlink:label="Locator_us-gaap_StockRepurchasedDuringPeriodShares_588" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_StatementLineItems_587" xlink:to="Locator_us-gaap_StockRepurchasedDuringPeriodShares_588" order="6.0" preferredLabel="http://www.xbrl.org/2009/role/negatedLabel" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementLineItems" xlink:label="Locator_us-gaap_StatementLineItems_589" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StockIssuedDuringPeriodValueStockOptionsExercised" xlink:label="Locator_us-gaap_StockIssuedDuringPeriodValueStockOptionsExercised_590" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_StatementLineItems_589" xlink:to="Locator_us-gaap_StockIssuedDuringPeriodValueStockOptionsExercised_590" order="7.0" preferredLabel="http://www.xbrl.org/2003/role/terseLabel" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementLineItems" xlink:label="Locator_us-gaap_StatementLineItems_591" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StockIssuedDuringPeriodSharesStockOptionsExercised" xlink:label="Locator_us-gaap_StockIssuedDuringPeriodSharesStockOptionsExercised_592" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_StatementLineItems_591" xlink:to="Locator_us-gaap_StockIssuedDuringPeriodSharesStockOptionsExercised_592" order="8.0" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementLineItems" xlink:label="Locator_us-gaap_StatementLineItems_593" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_ExcessTaxBenefitFromShareBasedCompensationOperatingActivities" xlink:label="Locator_us-gaap_ExcessTaxBenefitFromShareBasedCompensationOperatingActivities_594" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_StatementLineItems_593" xlink:to="Locator_us-gaap_ExcessTaxBenefitFromShareBasedCompensationOperatingActivities_594" order="9.0" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementLineItems" xlink:label="Locator_us-gaap_StatementLineItems_595" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StockOptionPlanExpense" xlink:label="Locator_us-gaap_StockOptionPlanExpense_596" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_StatementLineItems_595" xlink:to="Locator_us-gaap_StockOptionPlanExpense_596" order="10.0" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementLineItems" xlink:label="Locator_us-gaap_StatementLineItems_597" />
        <loc xlink:type="locator" xlink:href="mrln-20201231.xsd#mrln_PaymentOfReceivables" xlink:label="Locator_mrln_PaymentOfReceivables_598" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_StatementLineItems_597" xlink:to="Locator_mrln_PaymentOfReceivables_598" order="11.0" preferredLabel="http://www.xbrl.org/2003/role/terseLabel" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementLineItems" xlink:label="Locator_us-gaap_StatementLineItems_599" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StockIssuedDuringPeriodValueRestrictedStockAwardNetOfForfeitures" xlink:label="Locator_us-gaap_StockIssuedDuringPeriodValueRestrictedStockAwardNetOfForfeitures_600" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_StatementLineItems_599" xlink:to="Locator_us-gaap_StockIssuedDuringPeriodValueRestrictedStockAwardNetOfForfeitures_600" order="12.0" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementLineItems" xlink:label="Locator_us-gaap_StatementLineItems_601" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StockIssuedDuringPeriodSharesRestrictedStockAwardNetOfForfeitures" xlink:label="Locator_us-gaap_StockIssuedDuringPeriodSharesRestrictedStockAwardNetOfForfeitures_602" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_StatementLineItems_601" xlink:to="Locator_us-gaap_StockIssuedDuringPeriodSharesRestrictedStockAwardNetOfForfeitures_602" order="13.0" preferredLabel="http://www.xbrl.org/2003/role/terseLabel" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementLineItems" xlink:label="Locator_us-gaap_StatementLineItems_603" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_AllocatedShareBasedCompensationExpense" xlink:label="Locator_us-gaap_AllocatedShareBasedCompensationExpense_604" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_StatementLineItems_603" xlink:to="Locator_us-gaap_AllocatedShareBasedCompensationExpense_604" order="14.0" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementLineItems" xlink:label="Locator_us-gaap_StatementLineItems_605" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_OtherComprehensiveIncomeLossReclassificationAdjustmentFromAOCIOnDerivativesNetOfTax" xlink:label="Locator_us-gaap_OtherComprehensiveIncomeLossReclassificationAdjustmentFromAOCIOnDerivativesNetOfTax_606" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_StatementLineItems_605" xlink:to="Locator_us-gaap_OtherComprehensiveIncomeLossReclassificationAdjustmentFromAOCIOnDerivativesNetOfTax_606" order="15.0" preferredLabel="http://www.xbrl.org/2009/role/negatedLabel" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementLineItems" xlink:label="Locator_us-gaap_StatementLineItems_607" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_OtherComprehensiveIncomeUnrealizedHoldingGainLossOnSecuritiesArisingDuringPeriodNetOfTax" xlink:label="Locator_us-gaap_OtherComprehensiveIncomeUnrealizedHoldingGainLossOnSecuritiesArisingDuringPeriodNetOfTax_608" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_StatementLineItems_607" xlink:to="Locator_us-gaap_OtherComprehensiveIncomeUnrealizedHoldingGainLossOnSecuritiesArisingDuringPeriodNetOfTax_608" order="16.0" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementLineItems" xlink:label="Locator_us-gaap_StatementLineItems_609" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_ProfitLoss" xlink:label="Locator_us-gaap_ProfitLoss_610" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_StatementLineItems_609" xlink:to="Locator_us-gaap_ProfitLoss_610" order="17.0" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementLineItems" xlink:label="Locator_us-gaap_StatementLineItems_611" />
        <loc xlink:type="locator" xlink:href="mrln-20201231.xsd#mrln_EffectsOfAdoptingNewAccountingStandardsReclassificationFromAociToRetainedEarnings" xlink:label="Locator_mrln_EffectsOfAdoptingNewAccountingStandardsReclassificationFromAociToRetainedEarnings_612" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_StatementLineItems_611" xlink:to="Locator_mrln_EffectsOfAdoptingNewAccountingStandardsReclassificationFromAociToRetainedEarnings_612" order="18.0" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementLineItems" xlink:label="Locator_us-gaap_StatementLineItems_613" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_DividendsCommonStockCash" xlink:label="Locator_us-gaap_DividendsCommonStockCash_614" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_StatementLineItems_613" xlink:to="Locator_us-gaap_DividendsCommonStockCash_614" order="19.0" preferredLabel="http://www.xbrl.org/2009/role/negatedLabel" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementLineItems" xlink:label="Locator_us-gaap_StatementLineItems_577" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest" xlink:label="Locator_us-gaap_StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest_578" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_StatementLineItems_577" xlink:to="Locator_us-gaap_StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest_578" order="1.0" preferredLabel="http://www.xbrl.org/2003/role/periodStartLabel" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementLineItems" xlink:label="Locator_us-gaap_StatementLineItems_615" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest" xlink:label="Locator_us-gaap_StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest_616" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_StatementLineItems_615" xlink:to="Locator_us-gaap_StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest_616" order="20.0" preferredLabel="http://www.xbrl.org/2003/role/periodEndLabel" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest" xlink:label="Locator_us-gaap_StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest_621" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_AccountingStandardsUpdateExtensibleList" xlink:label="Locator_us-gaap_AccountingStandardsUpdateExtensibleList_622" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest_621" xlink:to="Locator_us-gaap_AccountingStandardsUpdateExtensibleList_622" order="1.0" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementLineItems" xlink:label="Locator_us-gaap_StatementLineItems_579" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_CommonStockSharesOutstanding" xlink:label="Locator_us-gaap_CommonStockSharesOutstanding_580" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_StatementLineItems_579" xlink:to="Locator_us-gaap_CommonStockSharesOutstanding_580" order="2.0" preferredLabel="http://www.xbrl.org/2003/role/periodStartLabel" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementLineItems" xlink:label="Locator_us-gaap_StatementLineItems_617" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_CommonStockSharesOutstanding" xlink:label="Locator_us-gaap_CommonStockSharesOutstanding_618" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_StatementLineItems_617" xlink:to="Locator_us-gaap_CommonStockSharesOutstanding_618" order="21.0" preferredLabel="http://www.xbrl.org/2003/role/periodEndLabel" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementTable" xlink:label="Locator_us-gaap_StatementTable_709" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_AdjustmentsForNewAccountingPronouncementsAxis" xlink:label="Locator_us-gaap_AdjustmentsForNewAccountingPronouncementsAxis_710" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_StatementTable_709" xlink:to="Locator_us-gaap_AdjustmentsForNewAccountingPronouncementsAxis_710" order="4.0" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_AdjustmentsForNewAccountingPronouncementsAxis" xlink:label="Locator_us-gaap_AdjustmentsForNewAccountingPronouncementsAxis_719" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_TypeOfAdoptionMember" xlink:label="Locator_us-gaap_TypeOfAdoptionMember_720" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_AdjustmentsForNewAccountingPronouncementsAxis_719" xlink:to="Locator_us-gaap_TypeOfAdoptionMember_720" order="1.0" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_TypeOfAdoptionMember" xlink:label="Locator_us-gaap_TypeOfAdoptionMember_711" />
        <loc xlink:type="locator" xlink:href="mrln-20201231.xsd#mrln_VariousAccountingStandardsAdoptedMember" xlink:label="Locator_mrln_VariousAccountingStandardsAdoptedMember_712" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_TypeOfAdoptionMember_711" xlink:to="Locator_mrln_VariousAccountingStandardsAdoptedMember_712" order="1.0" preferredLabel="http://www.xbrl.org/2003/role/terseLabel" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_TypeOfAdoptionMember" xlink:label="Locator_us-gaap_TypeOfAdoptionMember_713" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_AccountingStandardsUpdate201613Member" xlink:label="Locator_us-gaap_AccountingStandardsUpdate201613Member_714" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_TypeOfAdoptionMember_713" xlink:to="Locator_us-gaap_AccountingStandardsUpdate201613Member_714" order="2.0" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementOfStockholdersEquityAbstract" xlink:label="Locator_us-gaap_StatementOfStockholdersEquityAbstract_623" />
        <loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementTable" xlink:label="Locator_us-gaap_StatementTable_624" />
        <presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_StatementOfStockholdersEquityAbstract_623" xlink:to="Locator_us-gaap_StatementTable_624" order="1.0" />
    </presentationLink>

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
    line_error_adsh_3 = "0000018255-21-000004"
    line_error_adsh_4 = "0001562762-21-000101" # StatementConsolidatedStatementsOfStockholdersEquity
    line_error_adsh_5 = "0001564590-21-012964" # StatementConsolidatedStatementsOfCashFlows

    multiple_root_nodes_1 = "0000066756-21-000025" # several statements ending with role-name _1
    not_one_root_node_1 = "0000072903-21-000012"
    not_one_root_node_2 = "0000829224-21-000029" #
    not_one_root_node_3 = "0000920371-21-000042" #
    not_one_root_node_4 = "0001254699-21-000005" #
    #content = special_content_line_wrong

    content = get_pre_xml_content_by_adsh(not_one_root_node_4)
    parse_content(not_one_root_node_4, content)

    print("")

# problem -> tag kann mehrmals vorkommen -> siehe missing_line_15_in_IS -> in IS kommt NetIncomeLoss mehrmals vor
# es muss zwischen key und tag/label unterschieden werden
# bei beispiel ist terse und total  unterschiedlich..
# d.h. aber, dass mehrere locs aufs selbe presentation_arc zeigen
# entsprechend muss beim iterieren aufgepasst werden.
# es gibt anscheined locs, die haben kein presentation.. -> evtl. sollten wir nur presentation_beachten.