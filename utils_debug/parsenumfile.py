from src._02_xml import SecNumXmlParser

# special cases
# "huge text node"    file_nok ="d:/secprocessing/xml/2021-04-24/breit-20201231.xml"       # 0001564590-21-013907

# SELECT * FROM sec_report_processing WHERE preParseState is not "parsed" order by preParseState

if __name__ == '__main__':

    file_ok = "d:/secprocessing/xml/2021-04-24/legx-20171231.xml"


    # "xmlSAX2Characters: huge text node, line 114116, column 219 (<string>, line 114116)"
    # d:/secprocessing/xml/2021-04-24/lsi-10k_20201231_htm.xml 0001564590-21-007648
    # d:/secprocessing/xml/2021-04-24/adc-20201231x10k_htm.xml 0001558370-21-001212
    # d:/secprocessing/xml/2021-04-24/nnn-20201231_htm.xml     0000751364-21-000018
    file_nok ="d:/secprocessing/xml/2021-04-24/breit-20201231.xml" # 0001564590-21-013907

    with open(file_nok, "r", encoding="utf-8") as f:
        content = f.read()

        parser = SecNumXmlParser()
        df = parser.parse(content)
        parser.clean_for_financial_statement_dataset(df, "accnr")
        print("")