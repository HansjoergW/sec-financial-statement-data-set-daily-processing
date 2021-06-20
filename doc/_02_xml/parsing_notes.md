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
3.7. in parenthical or not can be treated as different "report" types
3.8. There is always a maximum number of 1 CP entry in the Zip
     There is always a maximum number of 1 BS and 1 BS inparenthesis in the Zip
3.9. Sometimes a filed report can also contain statements of subsidiaries. In these cases, the 
     name of the role of the presentation indicates that and therefore is longer as the role name of the
     main company. Therefore if there is more than one presentation of type (BS, IS, ..) the one with the shortest
     rolename has to be chosen.
3.10. sometimes, there is a title attribute present which contains the information of the statement type rather than the role
      e.g. 0001010412-21-000004 or 0001079973-21-000172
3.11. sometimes reports with/without paranthesis just differ by a p in the role, like
    '0001178913-21-000696'  - role="http://solaredge.com/role/sedg-cbs"
                            - role="http://solaredge.com/role/sedg-cbsp"
    '0001553350-21-000261'  - role="http://lightwavelogic.com/role/lwlg-bs"
                            - role="http://lightwavelogic.com/role/lwlg-bsp"
3.12. IS/CI sometimes only differ in the labels that are present while role and root are the same.
3.13. There are entries which can have two CI. One is a "normal" IS with one or more comprehensive entries.
      that one should be recognized as IS, and the second is a "normal" CI
      '0000766704-21-000018'



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

# Num-File-Parsing
## Contexts
1. context
1.1. a context is either for a period (with start and end date) or an instant
1.2. a context can contain segments.
1.3. a context with a segment with dimension dei:LegalEntityAxis indicates that it is a "sub-company" and the
     the node content defines the "coreg" entry
1.4. only contexts with no segment or ONE single dei:LegalEntityAxis segment are relevant for further processing and are 
     therefore written into the num.csv file
1.5. if the legalEntityAxis name ends with "Member" or "Domain", then 'Member' or 'Domain' is stripped just from the entry
1.6. if legalEntityAxis name has a "namespace" prefix, separated by a ":", then the prefix (including colon) is removed
1.7. the quarters are calculated from the start and end date of a period. as an approximation, the calculation is done
     with the formula "number of days between / (365.25 / 4)"
1.8. contexts are referenced from an entry containing tag and value by the attribute contextRef
1.9. the "ddate" for the entry in the csv file is calcaluted either from the instant or or the enddate of the context
1.10. the ddate is rounded to the nearest "end-of-month". Dates after the 15th day of a month are rounded to the end day of that month.
      days lower or equal to the 15th day of a month are rounded to the end of the previous month

## Units
2. unit
2.1. the used unit are defined in <unit> entities
2.2. a unit entity can either be a single measure or a relation, 
     identified by "divide" entity with a "unitNumerator" and a "unitDenominator"
2.3. unit measures are often prefixed by a namespace, separated by a ":". in this case, the prefix (including colon) is removed
2.4. if a unit is a relation (indicated by the "divde" entity), then the label used for the unit is written as <unitNumerator>/<unitDenumerator>
     unless the unitDenumerator is "shares". if the unitDenumerator is shares, then just the unitNumerator is used as label
2.5. the maximum lenght of a unit-label is 20 characters
2.6. unit are referenced from an entry conaining tag and value by the attribute unitRef

## Version / year
3. version / year
3.1. there are official and "company" namespaces. Official namespaces contain the domains  ['xbrl.org', 'sec.gov','fasb.org','w3.org', 'xbrl.ifrs.org']
3.2. if it is not an official namespace, then it is marked as "company" namespace. The version used für the company namespace
     is the adsh number of the report, without a year
3.2. versions based on "official" namespaces are extended with the year (separated by a /). The year is contained
     in the namespace url (ex: http://fasb.org/us-gaap/2020-01-31) 

## Values
3. values
3.1. the values in the csv are rounded to 4 decimals.
3.2. the values are rounded with the standard "mathematical" and not "scientific" rounding.  (https://realpython.com/python-rounding)
3.3. since not scientific rounding is used, the pandas, numpy and math.round functions of python cannot be used
3.4. inside a report, the same "tag" can appear with different precision (e.g. exact number, rounded to 1000s, rounded to millions).
     in the csv, only the most precise number is used
3.5. the attribute decimals indicate to which digit the a value is rounded in its presentation of the report.
     '0' or 'INF' indicate that it is the precise number, '-3' indicates that the shown value is rounded to 1000s,
     a '-6' indicates that is rounded to millions
     