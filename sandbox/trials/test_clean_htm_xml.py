
from pathlib import Path

CURRENT_PATH = Path(__file__).parent


"""
 lenght of files:
 - without stripping:                 4'719'409
 - with style stripping:              1'836'532
 - with emty style stripping:         1'422'631
 - with span 160 stripping:           1'252'258
 - with empty p stripping:            1'189'489
 - with class struooubg list:         1'185'265
 - with empty td stripping:           1'105'529
 - with remove empty span:            1'103'000
 - with remove empty lines/colspan:   1'019'060
 - with remove ixheader:                840'807
 - with remove span and div:            754'000

 

report : https://www.sec.gov/Archives/edgar/data/1475922/000095017024123110/0000950170-24-123110-index.htm


HTML: https://www.sec.gov/Archives/edgar/data/1475922/000095017024123110/pri-20240930.htm

Extract: https://www.sec.gov/Archives/edgar/data/1475922/000095017024123110/pri-20240930_htm.xml
   - Typen / Einheit
   - Values
   - Footnotes


Notes: <ix:header><ix:hidden> -> scheint viele infos zu haben, ist auch sehr gross..

"""

def test_clean_htm_xml():
    from secdaily._02_xml.parsing.htm._1_SecHtmXmlExtracting import SecHtmXmlExtractor

    file = CURRENT_PATH / "../data/html.txt"

    extractor = SecHtmXmlExtractor()
    data = extractor._strip_file(file.read_text())


    output_file = CURRENT_PATH / "../data/cleaned_html.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(data)

    print(data)
    print(len(data))



