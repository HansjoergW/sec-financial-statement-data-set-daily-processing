from src._02_xml import SecPreXmlParser

#special cases
# default namespace  xmlns="http://www.xbrl.org/2003/linkbase": d:/secprocessing/xml/2021-05-02/vgz-20210331_pre.xml

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

    with open(missing_line_15_in_IS, "r", encoding="utf-8") as f:
        content = f.read()

        parser = SecPreXmlParser()
        df = parser.parse(content)
        df_clean = parser.clean_for_financial_statement_dataset(df, "accnr")
        print(df_clean.shape) # die meisten attribute sind im index, daher ist die anzahl der spalten nur 3

# problem -> tag kann mehrmals vorkommen -> siehe missing_line_15_in_IS -> in IS kommt NetIncomeLoss mehrmals vor
# es muss zwischen key und tag/label unterschieden werden
# bei beispiel ist terse und total  unterschiedlich..
# d.h. aber, dass mehrere locs aufs selbe presentation_arc zeigen
# entsprechend muss beim iterieren aufgepasst werden.
# es gibt anscheined locs, die haben kein presentation.. -> evtl. sollten wir nur presentation_beachten.