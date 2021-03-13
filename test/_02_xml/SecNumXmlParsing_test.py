from _02_xml.SecNumXmlParsing import SecNumXmlParser

from typing import Dict, List, Tuple, Optional
from lxml import etree


xml_test_data = """<?xml version="1.0" encoding="utf-8"?>
<xbrl
  xml:lang="en-US"
  xmlns="http://www.xbrl.org/2003/instance"
  xmlns:aapl="http://www.apple.com/20200926"
  xmlns:country="http://xbrl.sec.gov/country/2020-01-31"
  xmlns:dei="http://xbrl.sec.gov/dei/2020-01-31"
  xmlns:iso4217="http://www.xbrl.org/2003/iso4217"
  xmlns:link="http://www.xbrl.org/2003/linkbase"
  xmlns:srt="http://fasb.org/srt/2020-01-31"
  xmlns:us-gaap="http://fasb.org/us-gaap/2020-01-31"
  xmlns:xbrldi="http://xbrl.org/2006/xbrldi"
  xmlns:xlink="http://www.w3.org/1999/xlink"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <link:schemaRef xlink:href="aapl-20200926.xsd" xlink:type="simple"/>
    <context id="i223bd574caab4f739f73936be6065c72_D20190929-20200926">
        <entity>
            <identifier scheme="http://www.sec.gov/CIK">0000320193</identifier>
        </entity>
        <period>
            <startDate>2019-09-29</startDate>
            <endDate>2020-09-26</endDate>
        </period>
    </context>
    <context id="i9f9a068454cf45bc8dabe3edf6e6b899_D20190929-20200926">
        <entity>
            <identifier scheme="http://www.sec.gov/CIK">0000320193</identifier>
            <segment>
                <xbrldi:explicitMember dimension="us-gaap:StatementClassOfStockAxis">us-gaap:CommonStockMember</xbrldi:explicitMember>
            </segment>
        </entity>
        <period>
            <startDate>2019-09-29</startDate>
            <endDate>2020-09-26</endDate>
        </period>
    </context>
    <context id="ic9b02aa81ea048e3b2d21ff1ff5ee96d_D20190929-20200926">
        <entity>
            <identifier scheme="http://www.sec.gov/CIK">0000320193</identifier>
            <segment>
                <xbrldi:explicitMember dimension="us-gaap:StatementClassOfStockAxis">aapl:A1.000NotesDue2022Member</xbrldi:explicitMember>
            </segment>
        </entity>
        <period>
            <startDate>2019-09-29</startDate>
            <endDate>2020-09-26</endDate>
        </period>
    </context>    
    <us-gaap:ResearchAndDevelopmentExpense
      contextRef="i223bd574caab4f739f73936be6065c72_D20190929-20200926"
      decimals="-6"
      id="id3VybDovL2RvY3MudjEvZG9jOmVmNzgxYWI1OGU0ZjRmY2FhODcyZGRiZDMwZGE0MGUxL3NlYzplZjc4MWFiNThlNGY0ZmNhYTg3MmRkYmQzMGRhNDBlMV84NS9mcmFnOjlhZmQ0ZDY0MDMwNjRjMmE5NDAxMWI4ZjFjMmE2Zjc1L3RhYmxlOjZjMTBjOWQ2ZjgzMTRhMGVhYjQ4NzAxNjQ2OTRkOWE2L3RhYmxlcmFuZ2U6NmMxMGM5ZDZmODMxNGEwZWFiNDg3MDE2NDY5NGQ5YTZfMTQtMS0xLTEtMA_4dc5e576-b829-4c9d-aa17-2472a6530aaa"
      unitRef="usd">18752000000</us-gaap:ResearchAndDevelopmentExpense>
    <us-gaap:SellingGeneralAndAdministrativeExpense
      contextRef="i223bd574caab4f739f73936be6065c72_D20190929-20200926"
      decimals="-6"
      id="id3VybDovL2RvY3MudjEvZG9jOmVmNzgxYWI1OGU0ZjRmY2FhODcyZGRiZDMwZGE0MGUxL3NlYzplZjc4MWFiNThlNGY0ZmNhYTg3MmRkYmQzMGRhNDBlMV84NS9mcmFnOjlhZmQ0ZDY0MDMwNjRjMmE5NDAxMWI4ZjFjMmE2Zjc1L3RhYmxlOjZjMTBjOWQ2ZjgzMTRhMGVhYjQ4NzAxNjQ2OTRkOWE2L3RhYmxlcmFuZ2U6NmMxMGM5ZDZmODMxNGEwZWFiNDg3MDE2NDY5NGQ5YTZfMTUtMS0xLTEtMA_d280f5de-ad11-460b-8898-ed13acbfb1a0"
      unitRef="usd">19916000000</us-gaap:SellingGeneralAndAdministrativeExpense>
    <us-gaap:NonoperatingIncomeExpense
      contextRef="i223bd574caab4f739f73936be6065c72_D20190929-20200926"
      decimals="-6"
      id="id3VybDovL2RvY3MudjEvZG9jOmVmNzgxYWI1OGU0ZjRmY2FhODcyZGRiZDMwZGE0MGUxL3NlYzplZjc4MWFiNThlNGY0ZmNhYTg3MmRkYmQzMGRhNDBlMV84NS9mcmFnOjlhZmQ0ZDY0MDMwNjRjMmE5NDAxMWI4ZjFjMmE2Zjc1L3RhYmxlOjZjMTBjOWQ2ZjgzMTRhMGVhYjQ4NzAxNjQ2OTRkOWE2L3RhYmxlcmFuZ2U6NmMxMGM5ZDZmODMxNGEwZWFiNDg3MDE2NDY5NGQ5YTZfMTktMS0xLTEtMA_c50c169e-f577-41b3-a704-fcfe7505b0eb"
      unitRef="usd">803000000</us-gaap:NonoperatingIncomeExpense>
    </xbrl>"""

xml_expected_stripped = """<?xml version="1.0"?><xbrl
  xml:lang="en-US"
  
  xmlns:aapl="http://www.apple.com/20200926"
  xmlns:country="http://xbrl.sec.gov/country/2020-01-31"
  xmlns:dei="http://xbrl.sec.gov/dei/2020-01-31"
  xmlns:iso4217="http://www.xbrl.org/2003/iso4217"
  xmlns:link="http://www.xbrl.org/2003/linkbase"
  xmlns:srt="http://fasb.org/srt/2020-01-31"
  xmlns:us-gaap="http://fasb.org/us-gaap/2020-01-31"
  xmlns:xbrldi="http://xbrl.org/2006/xbrldi"
  xmlns:xlink="http://www.w3.org/1999/xlink"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><context id="i223bd574caab4f739f73936be6065c72_D20190929-20200926"><startDate>2019-09-29</startDate><endDate>2020-09-26</endDate></context><context id="i9f9a068454cf45bc8dabe3edf6e6b899_D20190929-20200926"><segment><xbrldi:explicitMember dimension="us-gaap:StatementClassOfStockAxis">us-gaap:CommonStockMember</xbrldi:explicitMember></segment><startDate>2019-09-29</startDate><endDate>2020-09-26</endDate></context><context id="ic9b02aa81ea048e3b2d21ff1ff5ee96d_D20190929-20200926"><segment><xbrldi:explicitMember dimension="us-gaap:StatementClassOfStockAxis">aapl:A1.000NotesDue2022Member</xbrldi:explicitMember></segment><startDate>2019-09-29</startDate><endDate>2020-09-26</endDate></context><us-gaap:ResearchAndDevelopmentExpense
      contextRef="i223bd574caab4f739f73936be6065c72_D20190929-20200926"
      
      unitRef="usd">18752000000</us-gaap:ResearchAndDevelopmentExpense><us-gaap:SellingGeneralAndAdministrativeExpense
      contextRef="i223bd574caab4f739f73936be6065c72_D20190929-20200926"
      
      unitRef="usd">19916000000</us-gaap:SellingGeneralAndAdministrativeExpense><us-gaap:NonoperatingIncomeExpense
      contextRef="i223bd574caab4f739f73936be6065c72_D20190929-20200926"
      
      unitRef="usd">803000000</us-gaap:NonoperatingIncomeExpense></xbrl>"""


def test_find_last_day_of_month():
    parser = SecNumXmlParser()

    assert parser._find_last_day_of_month("2019-11-25") == "20191130"
    assert parser._find_last_day_of_month("2019-02-5") == "20190228"
    assert parser._find_last_day_of_month("2020-02-5") == "20200229"
    assert parser._find_last_day_of_month("2019-12-25") == "20191231"


def test_calculate_qtrs():
    parser = SecNumXmlParser()

    assert parser._calculate_qtrs("19", "09","20","09") == 4
    assert parser._calculate_qtrs("19", "06","19","09") == 1
    assert parser._calculate_qtrs("19", "10","20", "09") == 4
    assert parser._calculate_qtrs("19", "08", "19", "10") == 1


def test_strip_file():
    parser = SecNumXmlParser()

    content = parser._strip_file(xml_test_data)
    assert content == xml_expected_stripped


def test_read_contexts():
    parser = SecNumXmlParser()
    root = etree.fromstring(xml_expected_stripped)

    content: Dict[str, Tuple[str,int,Optional[list]]] = parser._read_contexts(root)
    assert len(content) == 3


def test_parse():
    parser = SecNumXmlParser()
    df = parser.parse(xml_test_data)
    print(len(df))






