
from pathlib import Path

CURRENT_PATH = Path(__file__).parent


"""
 lenght of files:
 - without stripping:         4'719'409
 - with style stripping:      1'836'532
 - with emty style stripping: 1'422'631
 - with span 160 stripping:   1'252'258
 - with empty p stripping:    1'189'489
 - with class struooubg list: 1'185'265
 - with empty td stripping:   1'105'529
 - with remove empty span:    1'103'000

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



