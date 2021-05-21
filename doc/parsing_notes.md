# Pre-File Parsing
## loc - presentation arc

1. order
1.1. order can be as int 1 or as 1.0
1.2. order can be start with 0 or 1. can be different between xml, between presentations or even between childs in a presentation
1.3. order can restart in any sublist or can restart with every presentation or can be continuous throughout the whole xml
1.4. there are also rarely cases where order contains a fraction like 10440.02 -> so order has to be processed as float

2. relation loc
2.1. version can only be generated from loc
2.2. there can be loc without a reference in presentation arc
2.1. several presentation arc can reference the same loc element. in this case the presentation should have different preferredLabels (ex. total and terse)

3. parent-child relation - line calculation
3.1. there are reports which add a running number to every occurence of to and from label, so the
     hierarchy cannot be evaluated without removing this suffixes. Problem these reports will appear as if they
     have many root nodes within a presentation (0000018255-21-000004)
3.2. it can be that the same to-label can exist under different parent-labels, as well as under the 
     same parent label. Therefore, in order to create a "key_tag" for that entry, the attributes to, from and order
     have to be used
3.3. there are some rare cases of statements (2 statements in 5500 reports for q1 2021) in a report for which have ambiguous parent-child defnition, meaning
     that the from-node could be connect to more than one to-node. In this case, the ambiguous entries have
     to be removed from the structure.
     examples: 0001562762-21-000101 # StatementConsolidatedStatementsOfStockholdersEquity
               0001564590-21-012964 # StatementConsolidatedStatementsOfCashFlows
3.4. there are some rare cases of statements (4 statements in 5500 reports for q1 2021) that contain multiple root_nodes.
     -> not supported yet.
     0000829224-21-000029 http://www.starbucks.com/role/DocumentAndEntityInformation
     0000920371-21-000042 http://www.simpsonfg.com/role/ConsolidatedStatementsofStockholdersEquityParenthetical
     0001254699-21-000005 http://www.qvc.com/role/ConsolidatedStatementsofCashFlows
     0001628280-21-002278 http://polaris.com/role/ConsolidatedStatementsOfCashFlows     

    
4. Evaluate of report
3.1. the naming is not always consistent
3.2. normally, there is a root node in presentation which indicates which stmt type it is, however, this is not
     always the case. so also the the "role" attribute of the presentation-parent-node has to be considered
3.3. Since the evaluation of the stmt has to be done on the basis of text-strings, we have to check for appropriate
     combinations of words, which may not be ambiguous, respectively the order in which the tests are done have
     consider it.
3.4. If there is no IS, but only a CI, then the report is labeled as IS: 0000016918-21-000010', 0000024090-21-000012" "0000034903-21-000020"
     However, in 2021 Q1 there was one Exception to that rule: 0001628280-21-003313
3.5. up-lowercase is not consistent, e.g. roles are sometimes in uppercase, somtimes in lowercase
3.6. sometimes there are empty presentionatLinks (not containing loc or prearc entries). These can be skipped.

5. calculating labels and version
5.1. label name and version is calculated from loc element:
5.1.1. with http namespace in xlink:href -> before # get ns and year -> us-gaap/2020
5.1.2. if no http in xlink:href-> "company tag" -> version -> adsh of the report
5.1.3. label starts after the first _ after the # in the xlink:href 
5.1.4. it happens rarely, that the tagname is None (in two stmts 'UN' for 0001564590-21-017096)

6. differences
6.1.    0000883984-21-000005 - hat zusätzliche Einträge im XML in den Statements
        StatementScenarioAxis und ScenarioUnspecifiedDomain von srt/2020 erscheinen nicht, erst ab StatementLineItems..

7. preferredlabels
7.1. there are also perdiodStartLabel and periodEndLabel in a CF for CashAndCashEq at beginning and end of period

