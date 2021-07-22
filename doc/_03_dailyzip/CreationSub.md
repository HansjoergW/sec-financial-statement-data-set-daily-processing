# Creation of Sub content

## Problems
### name 
It's not clear based on what the name is cleaned. mainly it is toUpper and the removal of \. 
However, there are four special cases:
adsh                    Name Zip                Name Xml
0000320193-21-000010    APPLE INC               APPLE INC.        
0001654954-21-002287    BK TECHNOLOGIES         BK TECHNOLOGIES CORP
0000004127-21-000013    SKYWORKS SOLUTIONS INC  SKYWORKS SOLUTIONS, INC.
0000003570-21-000039    CHENIERE ENERGY INC     CHENIERE ENERGY, INC.

It is not clear what the reules are, since there are entries which end with "INC.", or ", INC"
so it is not possible to just remove '.' and ',' as well. These would need to be hardcoded numbers.


### sic
There 15 entries which show different sic numbers, than the ones presented in the feed xml

### period
there are two entries which show a different period


