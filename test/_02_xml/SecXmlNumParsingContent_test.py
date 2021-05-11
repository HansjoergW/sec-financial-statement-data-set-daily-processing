from _02_xml.SecXmlNumParsing import SecNumXmlParser

import pandas as pd
import os

scriptpath = os.path.realpath(__file__ + "/..")
datafolder = scriptpath + "/data/"

# An example of a test which compares the content of the num-xml with the data of the same company contained in the
# quarterly num-txt file


text_file = datafolder +"num_apple_10k_2020_q4.txt"
xml_file = datafolder + "aapl-20200926_htm.xml"


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
        df_xml = parser.clean_for_financial_statement_dataset(df_xml, '0000320193-20-000096')
        df_xml.drop(['coreg', 'footnote'], axis=1, inplace=True)
        return df_xml


def compare():
    df_txt = read_txt()
    df_xml = read_xml()

    df_txt.set_index(['adsh', 'tag','version','ddate','qtrs'], inplace=True)
    df_txt.rename(columns = lambda x: x + '_txt', inplace=True)

    df_xml.rename(columns = lambda x: x + '_xml', inplace=True)


    df_merge = pd.merge(df_xml, df_txt, how="outer", left_index=True, right_index=True)

    df_diff = df_merge[(df_merge.uom_xml != df_merge.uom_txt)|(df_merge.value_xml != df_merge.value_txt)]
    # filtern von value spalten mit null
    df_diff = df_diff[~((df_merge.uom_xml == df_merge.uom_txt) & df_diff.value_xml.isnull() & df_diff.value_txt.isnull())]

    # wrongs = df_merge.iloc[df_merge.index.get_level_values('tag') == 'EffectiveIncomeTaxRateReconciliationAtFederalStatutoryIncomeTaxRate']
    # in case of apple, it looks as if there is an additional entry in the xml


    print("len xml: ", len(df_xml))
    print("len txt: ", len(df_txt))
    print("len mrg: ", len(df_merge))
    print("len dif: ", len(df_diff))


compare()



