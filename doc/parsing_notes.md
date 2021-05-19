# Pre-File Parsing
## loc - presentation arc

1. order
1.1. order can be as int 1 or as 1.0
1.2. order can be start with 0 or 1. can be different between xml, between presentations or even between childs in a presentation
1.3. order can restart in any sublist or can restart with every presentation or can be continuous throughout the whole xml
1.4. there are also rarely cases where order contains a fraction like 10440.02 -> so order has to be processed as float

2. relation loc - order
2.1. version can only be generated from loc
2.2. there can be loc without a reference in presentation arc
2.1. several presentation arc can reference the same loc element. in this case the presentation should have different preferredLabels (ex. total and terse)

3. parent-child relation
3.1 there are reports which add a running number to every occurence of to and from label, so the
    hierarchy cannot be evaluated without removing this suffixes. Problem these reports will appear as if they
    have many root nodes within a presentation (0000018255-21-000004)
    
4. Evaluate of report
3.1. the naming is not always consistent
3.2. normally, there is a root node in presentation which indicates which stmt type it is, however, this is not
     always the case. so also the the "role" attribute of the presentation-parent-node has to be considered
3.3. Since the evaluation of the stmt has to be done on the basis of text-strings, it is important to consider the order
     in which the check is done. For instance "IncomeStatement" would also be true in "ComprehensiveIncomeStatement"
3.4. If there is no IS, but only a CI, then the report is labeled as IS: 0000016918-21-000010', 0000024090-21-000012" "0000034903-21-000020"
     However, in 2021 Q1 there was one Exception to that rule: 0001628280-21-003313
3.5. up-lowercase is not consistent, e.g. roles are sometimes in uppercase, somtimes in lowercase

5. calculating labels and version
5.1. label name and version is calculated from loc element:
5.1.1. with http namespace in xlink:href -> before # get ns and year -> us-gaap/2020
5.1.2. if no http in xlink:href-> "company tag" -> version -> adsh of the report
5.1.3. label starts after the first _ after the # in the xlink:href 
5.1.4. it happens rarely, that the tagname is None (in two stmts 'UN' for 0001564590-21-017096)

6. differences
6.1.    0000883984-21-000005 - hat zusätzliche Einträge im XML in den Statements
        StatementScenarioAxis und ScenarioUnspecifiedDomain von srt/2020 erscheinen nicht, erst ab StatementLineItems..



