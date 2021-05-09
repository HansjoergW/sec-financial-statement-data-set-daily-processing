# Pre-File Parsing
## loc - presentation arc

1. order
1.1. order can be as int 1 or as 1.0
1.2. order can be start with 0 or 1. can be different between xml, between presentations or even between childs in a presentation
1.2. order can restart in any sublist or can restart with every presentation or can be continuous throughout the whole xml

2. relation loc - order
2.1. version can only be generated from loc
2.2. there can be loc without a reference in presentation arc
2.1. several presentation arc can reference the same loc element. in this case the presentation should have different preferredLabels (ex. total and terse)


