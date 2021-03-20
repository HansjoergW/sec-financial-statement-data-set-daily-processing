from _02_xml.SecNumXmlParsing import SecNumXmlParser

import pandas as pd

text_file = "c:/ieu/projects/sec_processing/data/num_apple_10k_2020_q4.txt"
xml_file = "c:/ieu/projects/sec_processing/data/aapl-20200926_htm.xml"


def read_txt() -> pd.DataFrame:
    df_txt = pd.read_csv(text_file, sep="\t", encoding="utf-8", header=0)
    df_txt['ddate'] = df_txt.ddate.apply(str)
    df_txt['qtrs']  = df_txt.qtrs.apply(int)

    df_txt.drop(['coreg', 'footnote'], axis=1, inplace=True)
    return df_txt


def read_xml() -> pd.DataFrame:
    parser = SecNumXmlParser()
    with open(xml_file, "r", encoding="utf-8") as f:
        xml_content = f.read()
        df_xml = parser.parse(xml_content)
        df_xml = parser.clean_for_pure_num(df_xml, '0000320193-20-000096')
        df_xml.drop(['coreg', 'footnote'], axis=1, inplace=True)
        return df_xml


def compare():
    df_txt = read_txt()
    df_xml = read_xml()

    df_txt.set_index(['adsh', 'tag','version','ddate','qtrs'], inplace=True)
    df_txt.rename(columns = lambda x: x + '_txt', inplace=True)

    df_xml.set_index(['adsh', 'tag','version','ddate','qtrs'], inplace=True)
    df_xml.rename(columns = lambda x: x + '_xml', inplace=True)

    df_xml.sort_values('decimals_xml', inplace=True)
    df_double_index_mask = df_xml.index.duplicated(keep='first')
    df_xml_no_duplicated = df_xml[~df_double_index_mask]

    df_merge = pd.merge(df_txt, df_xml_no_duplicated, how="outer", left_index=True, right_index=True)

    # diff muss noch erweitert werden
    df_diff = df_merge[(df_merge.uom_xml != df_merge.uom_txt)|(df_merge.value_xml != df_merge.value_txt)]

    print("len xml: ", len(df_xml))
    print("len txt: ", len(df_txt))
    print("len mrg: ", len(df_merge))
    print("len dif: ", len(df_diff))


compare()



