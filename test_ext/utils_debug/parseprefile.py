from _02_xml.SecXmlPreParsing import SecPreXmlParser
from _00_common.DebugUtils import DataAccessByAdshTool

#special cases
# default namespace  xmlns="http://www.xbrl.org/2003/linkbase": d:/secprocessing/xml/2021-05-02/vgz-20210331_pre.xml

workdir = "d:/secprocessing/"

special_content_line_wrong = """<?xml version="1.0" encoding="UTF-8"?>
<link:linkbase xmlns:link="http://www.xbrl.org/2003/linkbase" xmlns:xbrldt="http://xbrl.org/2005/xbrldt" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.xbrl.org/2003/linkbase http://www.xbrl.org/2003/xbrl-linkbase-2003-12-31.xsd">
<presentationLink xlink:type="extended" xlink:role="http://www.catofashions.com/role/StatementConsolidatedStatementsOfCashFlows">
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementOfCashFlowsAbstract" xlink:label="Locator_us-gaap_StatementOfCashFlowsAbstract_359" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_NetCashProvidedByUsedInOperatingActivitiesAbstract" xlink:label="Locator_us-gaap_NetCashProvidedByUsedInOperatingActivitiesAbstract_360" />
	
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_StatementOfCashFlowsAbstract_359" xlink:to="Locator_us-gaap_NetCashProvidedByUsedInOperatingActivitiesAbstract_360" order="1.0" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_NetCashProvidedByUsedInOperatingActivitiesAbstract" xlink:label="Locator_us-gaap_NetCashProvidedByUsedInOperatingActivitiesAbstract_379" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_NetIncomeLoss" xlink:label="Locator_us-gaap_NetIncomeLoss_380" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_NetCashProvidedByUsedInOperatingActivitiesAbstract_379" xlink:to="Locator_us-gaap_NetIncomeLoss_380" order="1.0" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_NetCashProvidedByUsedInOperatingActivitiesAbstract" xlink:label="Locator_us-gaap_NetCashProvidedByUsedInOperatingActivitiesAbstract_381" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivitiesAbstract" xlink:label="Locator_us-gaap_AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivitiesAbstract_382" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_NetCashProvidedByUsedInOperatingActivitiesAbstract_381" xlink:to="Locator_us-gaap_AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivitiesAbstract_382" order="2.0" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivitiesAbstract" xlink:label="Locator_us-gaap_AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivitiesAbstract_383" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_DepreciationAndAmortization" xlink:label="Locator_us-gaap_DepreciationAndAmortization_384" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivitiesAbstract_383" xlink:to="Locator_us-gaap_DepreciationAndAmortization_384" order="1.0" preferredLabel="http://www.xbrl.org/2003/role/terseLabel" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivitiesAbstract" xlink:label="Locator_us-gaap_AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivitiesAbstract_385" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_ProvisionForDoubtfulAccounts" xlink:label="Locator_us-gaap_ProvisionForDoubtfulAccounts_386" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivitiesAbstract_385" xlink:to="Locator_us-gaap_ProvisionForDoubtfulAccounts_386" order="2.0" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivitiesAbstract" xlink:label="Locator_us-gaap_AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivitiesAbstract_387" />
	<loc xlink:type="locator" xlink:href="cato-20210130.xsd#cato_PurchasePremiumAndPremiumAmortization" xlink:label="Locator_cato_PurchasePremiumAndPremiumAmortization_388" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivitiesAbstract_387" xlink:to="Locator_cato_PurchasePremiumAndPremiumAmortization_388" order="3.0" preferredLabel="http://www.xbrl.org/2003/role/verboseLabel" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivitiesAbstract" xlink:label="Locator_us-gaap_AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivitiesAbstract_389" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_GainsLossesOnSalesOfAssets" xlink:label="Locator_us-gaap_GainsLossesOnSalesOfAssets_390" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivitiesAbstract_389" xlink:to="Locator_us-gaap_GainsLossesOnSalesOfAssets_390" order="4.0" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivitiesAbstract" xlink:label="Locator_us-gaap_AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivitiesAbstract_391" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_ShareBasedCompensation" xlink:label="Locator_us-gaap_ShareBasedCompensation_392" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivitiesAbstract_391" xlink:to="Locator_us-gaap_ShareBasedCompensation_392" order="5.0" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivitiesAbstract" xlink:label="Locator_us-gaap_AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivitiesAbstract_393" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_ExcessTaxBenefitFromShareBasedCompensationOperatingActivities" xlink:label="Locator_us-gaap_ExcessTaxBenefitFromShareBasedCompensationOperatingActivities_394" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivitiesAbstract_393" xlink:to="Locator_us-gaap_ExcessTaxBenefitFromShareBasedCompensationOperatingActivities_394" order="6.0" preferredLabel="http://www.xbrl.org/2009/role/negatedLabel" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivitiesAbstract" xlink:label="Locator_us-gaap_AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivitiesAbstract_395" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_DeferredIncomeTaxExpenseBenefit" xlink:label="Locator_us-gaap_DeferredIncomeTaxExpenseBenefit_396" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivitiesAbstract_395" xlink:to="Locator_us-gaap_DeferredIncomeTaxExpenseBenefit_396" order="7.0" preferredLabel="http://www.xbrl.org/2003/role/terseLabel" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivitiesAbstract" xlink:label="Locator_us-gaap_AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivitiesAbstract_397" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_GainLossOnSaleOfPropertyPlantEquipment" xlink:label="Locator_us-gaap_GainLossOnSaleOfPropertyPlantEquipment_398" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivitiesAbstract_397" xlink:to="Locator_us-gaap_GainLossOnSaleOfPropertyPlantEquipment_398" order="8.0" preferredLabel="http://www.xbrl.org/2009/role/negatedLabel" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivitiesAbstract" xlink:label="Locator_us-gaap_AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivitiesAbstract_399" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_ImpairmentOfLeasehold" xlink:label="Locator_us-gaap_ImpairmentOfLeasehold_400" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivitiesAbstract_399" xlink:to="Locator_us-gaap_ImpairmentOfLeasehold_400" order="9.0" preferredLabel="http://www.xbrl.org/2009/role/negatedLabel" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivitiesAbstract" xlink:label="Locator_us-gaap_AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivitiesAbstract_401" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_IncreaseDecreaseInOperatingCapitalAbstract" xlink:label="Locator_us-gaap_IncreaseDecreaseInOperatingCapitalAbstract_402" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivitiesAbstract_401" xlink:to="Locator_us-gaap_IncreaseDecreaseInOperatingCapitalAbstract_402" order="10.0" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_IncreaseDecreaseInOperatingCapitalAbstract" xlink:label="Locator_us-gaap_IncreaseDecreaseInOperatingCapitalAbstract_405" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_IncreaseDecreaseInAccountsAndOtherReceivables" xlink:label="Locator_us-gaap_IncreaseDecreaseInAccountsAndOtherReceivables_406" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_IncreaseDecreaseInOperatingCapitalAbstract_405" xlink:to="Locator_us-gaap_IncreaseDecreaseInAccountsAndOtherReceivables_406" order="1.0" preferredLabel="http://www.xbrl.org/2009/role/negatedLabel" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_IncreaseDecreaseInOperatingCapitalAbstract" xlink:label="Locator_us-gaap_IncreaseDecreaseInOperatingCapitalAbstract_407" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_IncreaseDecreaseInRetailRelatedInventories" xlink:label="Locator_us-gaap_IncreaseDecreaseInRetailRelatedInventories_408" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_IncreaseDecreaseInOperatingCapitalAbstract_407" xlink:to="Locator_us-gaap_IncreaseDecreaseInRetailRelatedInventories_408" order="2.0" preferredLabel="http://www.xbrl.org/2009/role/negatedLabel" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_IncreaseDecreaseInOperatingCapitalAbstract" xlink:label="Locator_us-gaap_IncreaseDecreaseInOperatingCapitalAbstract_409" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_IncreaseDecreaseInOtherOperatingAssets" xlink:label="Locator_us-gaap_IncreaseDecreaseInOtherOperatingAssets_410" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_IncreaseDecreaseInOperatingCapitalAbstract_409" xlink:to="Locator_us-gaap_IncreaseDecreaseInOtherOperatingAssets_410" order="3.0" preferredLabel="http://www.xbrl.org/2009/role/negatedLabel" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_IncreaseDecreaseInOperatingCapitalAbstract" xlink:label="Locator_us-gaap_IncreaseDecreaseInOperatingCapitalAbstract_411" />
	<loc xlink:type="locator" xlink:href="cato-20210130.xsd#cato_Changeoperatingleaseassetandliabilitiesnet" xlink:label="Locator_cato_Changeoperatingleaseassetandliabilitiesnet_412" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_IncreaseDecreaseInOperatingCapitalAbstract_411" xlink:to="Locator_cato_Changeoperatingleaseassetandliabilitiesnet_412" order="4.0" preferredLabel="http://www.xbrl.org/2003/role/verboseLabel" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_IncreaseDecreaseInOperatingCapitalAbstract" xlink:label="Locator_us-gaap_IncreaseDecreaseInOperatingCapitalAbstract_413" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_IncreaseDecreaseInAccruedIncomeTaxesPayable" xlink:label="Locator_us-gaap_IncreaseDecreaseInAccruedIncomeTaxesPayable_414" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_IncreaseDecreaseInOperatingCapitalAbstract_413" xlink:to="Locator_us-gaap_IncreaseDecreaseInAccruedIncomeTaxesPayable_414" order="5.0" preferredLabel="http://www.xbrl.org/2003/role/terseLabel" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_IncreaseDecreaseInOperatingCapitalAbstract" xlink:label="Locator_us-gaap_IncreaseDecreaseInOperatingCapitalAbstract_415" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_IncreaseDecreaseInAccountsPayable" xlink:label="Locator_us-gaap_IncreaseDecreaseInAccountsPayable_416" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_IncreaseDecreaseInOperatingCapitalAbstract_415" xlink:to="Locator_us-gaap_IncreaseDecreaseInAccountsPayable_416" order="6.0" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivitiesAbstract" xlink:label="Locator_us-gaap_AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivitiesAbstract_403" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_NetCashProvidedByUsedInOperatingActivities" xlink:label="Locator_us-gaap_NetCashProvidedByUsedInOperatingActivities_404" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivitiesAbstract_403" xlink:to="Locator_us-gaap_NetCashProvidedByUsedInOperatingActivities_404" order="11.0" preferredLabel="http://www.xbrl.org/2003/role/totalLabel" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementOfCashFlowsAbstract" xlink:label="Locator_us-gaap_StatementOfCashFlowsAbstract_361" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_NetCashProvidedByUsedInInvestingActivitiesAbstract" xlink:label="Locator_us-gaap_NetCashProvidedByUsedInInvestingActivitiesAbstract_362" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_StatementOfCashFlowsAbstract_361" xlink:to="Locator_us-gaap_NetCashProvidedByUsedInInvestingActivitiesAbstract_362" order="2.0" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_NetCashProvidedByUsedInInvestingActivitiesAbstract" xlink:label="Locator_us-gaap_NetCashProvidedByUsedInInvestingActivitiesAbstract_417" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_PaymentsToAcquirePropertyPlantAndEquipment" xlink:label="Locator_us-gaap_PaymentsToAcquirePropertyPlantAndEquipment_418" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_NetCashProvidedByUsedInInvestingActivitiesAbstract_417" xlink:to="Locator_us-gaap_PaymentsToAcquirePropertyPlantAndEquipment_418" order="1.0" preferredLabel="http://www.xbrl.org/2009/role/negatedLabel" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_NetCashProvidedByUsedInInvestingActivitiesAbstract" xlink:label="Locator_us-gaap_NetCashProvidedByUsedInInvestingActivitiesAbstract_419" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_PaymentsToAcquireShortTermInvestments" xlink:label="Locator_us-gaap_PaymentsToAcquireShortTermInvestments_420" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_NetCashProvidedByUsedInInvestingActivitiesAbstract_419" xlink:to="Locator_us-gaap_PaymentsToAcquireShortTermInvestments_420" order="2.0" preferredLabel="http://www.xbrl.org/2009/role/negatedLabel" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_NetCashProvidedByUsedInInvestingActivitiesAbstract" xlink:label="Locator_us-gaap_NetCashProvidedByUsedInInvestingActivitiesAbstract_421" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_ProceedsFromSaleMaturityAndCollectionsOfInvestments" xlink:label="Locator_us-gaap_ProceedsFromSaleMaturityAndCollectionsOfInvestments_422" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_NetCashProvidedByUsedInInvestingActivitiesAbstract_421" xlink:to="Locator_us-gaap_ProceedsFromSaleMaturityAndCollectionsOfInvestments_422" order="3.0" preferredLabel="http://www.xbrl.org/2003/role/positiveVerboseLabel" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_NetCashProvidedByUsedInInvestingActivitiesAbstract" xlink:label="Locator_us-gaap_NetCashProvidedByUsedInInvestingActivitiesAbstract_423" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_PaymentsToAcquireProjects" xlink:label="Locator_us-gaap_PaymentsToAcquireProjects_424" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_NetCashProvidedByUsedInInvestingActivitiesAbstract_423" xlink:to="Locator_us-gaap_PaymentsToAcquireProjects_424" order="4.0" preferredLabel="http://www.xbrl.org/2009/role/negatedLabel" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_NetCashProvidedByUsedInInvestingActivitiesAbstract" xlink:label="Locator_us-gaap_NetCashProvidedByUsedInInvestingActivitiesAbstract_425" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_ProceedsFromSaleOfInvestmentProjects" xlink:label="Locator_us-gaap_ProceedsFromSaleOfInvestmentProjects_426" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_NetCashProvidedByUsedInInvestingActivitiesAbstract_425" xlink:to="Locator_us-gaap_ProceedsFromSaleOfInvestmentProjects_426" order="5.0" preferredLabel="http://www.xbrl.org/2009/role/negatedLabel" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_NetCashProvidedByUsedInInvestingActivitiesAbstract" xlink:label="Locator_us-gaap_NetCashProvidedByUsedInInvestingActivitiesAbstract_427" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_IncreaseDecreaseInRestrictedCash" xlink:label="Locator_us-gaap_IncreaseDecreaseInRestrictedCash_428" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_NetCashProvidedByUsedInInvestingActivitiesAbstract_427" xlink:to="Locator_us-gaap_IncreaseDecreaseInRestrictedCash_428" order="6.0" preferredLabel="http://www.xbrl.org/2009/role/negatedLabel" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_NetCashProvidedByUsedInInvestingActivitiesAbstract" xlink:label="Locator_us-gaap_NetCashProvidedByUsedInInvestingActivitiesAbstract_429" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_NetCashProvidedByUsedInInvestingActivities" xlink:label="Locator_us-gaap_NetCashProvidedByUsedInInvestingActivities_430" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_NetCashProvidedByUsedInInvestingActivitiesAbstract_429" xlink:to="Locator_us-gaap_NetCashProvidedByUsedInInvestingActivities_430" order="7.0" preferredLabel="http://www.xbrl.org/2003/role/totalLabel" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementOfCashFlowsAbstract" xlink:label="Locator_us-gaap_StatementOfCashFlowsAbstract_363" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_NetCashProvidedByUsedInFinancingActivitiesAbstract" xlink:label="Locator_us-gaap_NetCashProvidedByUsedInFinancingActivitiesAbstract_364" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_StatementOfCashFlowsAbstract_363" xlink:to="Locator_us-gaap_NetCashProvidedByUsedInFinancingActivitiesAbstract_364" order="3.0" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_NetCashProvidedByUsedInFinancingActivitiesAbstract" xlink:label="Locator_us-gaap_NetCashProvidedByUsedInFinancingActivitiesAbstract_431" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_ProceedsFromRepaymentsOfBankOverdrafts" xlink:label="Locator_us-gaap_ProceedsFromRepaymentsOfBankOverdrafts_432" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_NetCashProvidedByUsedInFinancingActivitiesAbstract_431" xlink:to="Locator_us-gaap_ProceedsFromRepaymentsOfBankOverdrafts_432" order="1.0" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_NetCashProvidedByUsedInFinancingActivitiesAbstract" xlink:label="Locator_us-gaap_NetCashProvidedByUsedInFinancingActivitiesAbstract_433" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_PaymentsOfDividends" xlink:label="Locator_us-gaap_PaymentsOfDividends_434" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_NetCashProvidedByUsedInFinancingActivitiesAbstract_433" xlink:to="Locator_us-gaap_PaymentsOfDividends_434" order="2.0" preferredLabel="http://www.xbrl.org/2009/role/negatedLabel" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_NetCashProvidedByUsedInFinancingActivitiesAbstract" xlink:label="Locator_us-gaap_NetCashProvidedByUsedInFinancingActivitiesAbstract_435" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_PaymentsForRepurchaseOfCommonStock" xlink:label="Locator_us-gaap_PaymentsForRepurchaseOfCommonStock_436" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_NetCashProvidedByUsedInFinancingActivitiesAbstract_435" xlink:to="Locator_us-gaap_PaymentsForRepurchaseOfCommonStock_436" order="3.0" preferredLabel="http://www.xbrl.org/2009/role/negatedLabel" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_NetCashProvidedByUsedInFinancingActivitiesAbstract" xlink:label="Locator_us-gaap_NetCashProvidedByUsedInFinancingActivitiesAbstract_437" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_ProceedsFromLinesOfCredit" xlink:label="Locator_us-gaap_ProceedsFromLinesOfCredit_438" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_NetCashProvidedByUsedInFinancingActivitiesAbstract_437" xlink:to="Locator_us-gaap_ProceedsFromLinesOfCredit_438" order="4.0" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_NetCashProvidedByUsedInFinancingActivitiesAbstract" xlink:label="Locator_us-gaap_NetCashProvidedByUsedInFinancingActivitiesAbstract_439" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_RepaymentsOfLinesOfCredit" xlink:label="Locator_us-gaap_RepaymentsOfLinesOfCredit_440" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_NetCashProvidedByUsedInFinancingActivitiesAbstract_439" xlink:to="Locator_us-gaap_RepaymentsOfLinesOfCredit_440" order="5.0" preferredLabel="http://www.xbrl.org/2009/role/negatedLabel" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_NetCashProvidedByUsedInFinancingActivitiesAbstract" xlink:label="Locator_us-gaap_NetCashProvidedByUsedInFinancingActivitiesAbstract_441" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_ProceedsFromStockPlans" xlink:label="Locator_us-gaap_ProceedsFromStockPlans_442" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_NetCashProvidedByUsedInFinancingActivitiesAbstract_441" xlink:to="Locator_us-gaap_ProceedsFromStockPlans_442" order="6.0" preferredLabel="http://www.xbrl.org/2003/role/terseLabel" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_NetCashProvidedByUsedInFinancingActivitiesAbstract" xlink:label="Locator_us-gaap_NetCashProvidedByUsedInFinancingActivitiesAbstract_443" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_ExcessTaxBenefitFromShareBasedCompensationFinancingActivities" xlink:label="Locator_us-gaap_ExcessTaxBenefitFromShareBasedCompensationFinancingActivities_444" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_NetCashProvidedByUsedInFinancingActivitiesAbstract_443" xlink:to="Locator_us-gaap_ExcessTaxBenefitFromShareBasedCompensationFinancingActivities_444" order="7.0" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_NetCashProvidedByUsedInFinancingActivitiesAbstract" xlink:label="Locator_us-gaap_NetCashProvidedByUsedInFinancingActivitiesAbstract_445" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_ProceedsFromStockOptionsExercised" xlink:label="Locator_us-gaap_ProceedsFromStockOptionsExercised_446" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_NetCashProvidedByUsedInFinancingActivitiesAbstract_445" xlink:to="Locator_us-gaap_ProceedsFromStockOptionsExercised_446" order="8.0" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_NetCashProvidedByUsedInFinancingActivitiesAbstract" xlink:label="Locator_us-gaap_NetCashProvidedByUsedInFinancingActivitiesAbstract_447" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_NetCashProvidedByUsedInFinancingActivities" xlink:label="Locator_us-gaap_NetCashProvidedByUsedInFinancingActivities_448" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_NetCashProvidedByUsedInFinancingActivitiesAbstract_447" xlink:to="Locator_us-gaap_NetCashProvidedByUsedInFinancingActivities_448" order="9.0" preferredLabel="http://www.xbrl.org/2003/role/totalLabel" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementOfCashFlowsAbstract" xlink:label="Locator_us-gaap_StatementOfCashFlowsAbstract_365" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_CashAndCashEquivalentsPeriodIncreaseDecrease" xlink:label="Locator_us-gaap_CashAndCashEquivalentsPeriodIncreaseDecrease_366" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_StatementOfCashFlowsAbstract_365" xlink:to="Locator_us-gaap_CashAndCashEquivalentsPeriodIncreaseDecrease_366" order="4.0" preferredLabel="http://www.xbrl.org/2003/role/totalLabel" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementOfCashFlowsAbstract" xlink:label="Locator_us-gaap_StatementOfCashFlowsAbstract_369" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_EffectOfExchangeRateOnCash" xlink:label="Locator_us-gaap_EffectOfExchangeRateOnCash_370" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_StatementOfCashFlowsAbstract_369" xlink:to="Locator_us-gaap_EffectOfExchangeRateOnCash_370" order="6.0" preferredLabel="http://www.xbrl.org/2003/role/verboseLabel" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementOfCashFlowsAbstract" xlink:label="Locator_us-gaap_StatementOfCashFlowsAbstract_367" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents" xlink:label="Locator_us-gaap_CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents_368" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_StatementOfCashFlowsAbstract_367" xlink:to="Locator_us-gaap_CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents_368" order="5.0" preferredLabel="http://www.xbrl.org/2003/role/periodStartLabel" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementOfCashFlowsAbstract" xlink:label="Locator_us-gaap_StatementOfCashFlowsAbstract_371" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents" xlink:label="Locator_us-gaap_CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents_372" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_StatementOfCashFlowsAbstract_371" xlink:to="Locator_us-gaap_CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents_372" order="7.0" preferredLabel="http://www.xbrl.org/2003/role/periodEndLabel" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementOfCashFlowsAbstract" xlink:label="Locator_us-gaap_StatementOfCashFlowsAbstract_373" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_CapitalExpendituresIncurredButNotYetPaid" xlink:label="Locator_us-gaap_CapitalExpendituresIncurredButNotYetPaid_374" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_StatementOfCashFlowsAbstract_373" xlink:to="Locator_us-gaap_CapitalExpendituresIncurredButNotYetPaid_374" order="8.0" preferredLabel="http://www.xbrl.org/2003/role/verboseLabel" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementOfCashFlowsAbstract" xlink:label="Locator_us-gaap_StatementOfCashFlowsAbstract_375" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_TransferToInvestments" xlink:label="Locator_us-gaap_TransferToInvestments_376" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_StatementOfCashFlowsAbstract_375" xlink:to="Locator_us-gaap_TransferToInvestments_376" order="9.0" preferredLabel="http://www.xbrl.org/2003/role/verboseLabel" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StatementOfCashFlowsAbstract" xlink:label="Locator_us-gaap_StatementOfCashFlowsAbstract_377" />
	<loc xlink:type="locator" xlink:href="http://xbrl.fasb.org/us-gaap/2020/elts/us-gaap-2020-01-31.xsd#us-gaap_StockIssued1" xlink:label="Locator_us-gaap_StockIssued1_378" />
	<presentationArc xlink:type="arc" xlink:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xlink:from="Locator_us-gaap_StatementOfCashFlowsAbstract_377" xlink:to="Locator_us-gaap_StockIssued1_378" order="10.0" preferredLabel="http://www.xbrl.org/2003/role/verboseLabel" />
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

    content = special_content_line_wrong
    #content = get_pre_xml_content_by_adsh(line_error_adsh_3)

    parse_content(line_error_adsh_3, content)

    print("")

# problem -> tag kann mehrmals vorkommen -> siehe missing_line_15_in_IS -> in IS kommt NetIncomeLoss mehrmals vor
# es muss zwischen key und tag/label unterschieden werden
# bei beispiel ist terse und total  unterschiedlich..
# d.h. aber, dass mehrere locs aufs selbe presentation_arc zeigen
# entsprechend muss beim iterieren aufgepasst werden.
# es gibt anscheined locs, die haben kein presentation.. -> evtl. sollten wir nur presentation_beachten.