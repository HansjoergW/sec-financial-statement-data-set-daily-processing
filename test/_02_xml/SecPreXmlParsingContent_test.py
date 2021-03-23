from _02_xml.SecPreXmlParsing import SecPreXmlParser

import pandas as pd


# An example of a test which compares the content of the prex-xml with the data of the same company contained in the
# quarterly pre-txt file

text_file = "c:/ieu/projects/sec_processing/data/pre_apple_10k_2020_q4.txt"
xml_file = "c:/ieu/projects/sec_processing/data/aapl-20200926_pre.xml"

def read_txt() -> pd.DataFrame:
    df_txt = pd.read_csv(text_file, sep="\t", encoding="utf-8", header=0)
    # df_txt['ddate'] = df_txt.ddate.apply(str)
    # df_txt['qtrs']  = df_txt.qtrs.apply(int)
    #
    df_txt.drop(['plabel'], axis=1, inplace=True)
    return df_txt


def read_xml() -> pd.DataFrame:
    parser = SecPreXmlParser()
    with open(xml_file, "r", encoding="utf-8") as f:
        xml_content = f.read()
        df_xml = parser.parse(xml_content, "H")
        df_xml = parser.clean_for_pure_pre(df_xml, '0000320193-20-000096')
        return df_xml


def compare():
    df_txt = read_txt()
    df_xml = read_xml()

    df_txt.set_index(['adsh', 'tag','version', 'report', 'line', 'stmt'], inplace=True)
    df_txt.rename(columns = lambda x: x + '_txt', inplace=True)

    df_xml.rename(columns = lambda x: x + '_xml', inplace=True)

    df_merge = pd.merge(df_txt, df_xml, how="outer", left_index=True, right_index=True)

    df_diff = df_merge[(df_merge.negating_xml != df_merge.negating_txt)|(df_merge.inpth_xml != df_merge.inpth_txt)|(df_merge.rfile_xml != df_merge.rfile_txt)]

    # nur noch EQ Eintrag vorhanden. Es scheint als wäre EQ 2mal vorhanden
    print("len xml: ", len(df_xml))
    print("len txt: ", len(df_txt))
    print("len mrg: ", len(df_merge))
    print("len dif: ", len(df_diff))


compare()