from pathlib import Path
from typing import List, Optional, Tuple

import pandas as pd
import pytest
from numpy import float64, int64
from pandas.testing import assert_frame_equal
from secdaily._00_common.SecFileUtils import read_content_from_zip, read_file_from_zip
from secdaily._02_xml.parsing.SecXmlLabParsing import SecLabXmlParser
from secdaily._02_xml.parsing.SecXmlNumParsing import SecNumXmlParser
from secdaily._02_xml.parsing.SecXmlParsingBase import SecError
from secdaily._02_xml.parsing.SecXmlPreParsing import SecPreXmlParser
from secdaily._03_secstyle.formatting.SECPreNumFormatting import SECPreNumFormatter

CURRENT_PATH = Path(__file__).parent
SANDBOXDATA_PATH = CURRENT_PATH.parent.parent / 'data'
TESTDATA_PATH = CURRENT_PATH /  'testdata'
RAW_XML_PATH = TESTDATA_PATH / 'rawxml'

APPLE_2024_10K_ADSH = "0000320193-24-000123"

@pytest.fixture
def sec_num_xml_parser() -> SecNumXmlParser:
    return SecNumXmlParser()


@pytest.fixture
def sec_pre_xml_parser() -> SecPreXmlParser:
    return SecPreXmlParser()


@pytest.fixture
def print_full_table():
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)

        yield

        pd.reset_option('display.max_rows')
        pd.reset_option('display.max_columns')
        pd.reset_option('display.width')
        pd.reset_option('display.max_colwidth')


@pytest.fixture
def pre_parsed_df(sec_pre_xml_parser) -> pd.DataFrame:

    content_pre = read_content_from_zip(str(RAW_XML_PATH / '0000320193-24-000123-aapl-20240928_pre.xml'))

    parsed_df, _ = sec_pre_xml_parser.parse(adsh=APPLE_2024_10K_ADSH, data=content_pre)

    cleaned_df = sec_pre_xml_parser.clean_for_financial_statement_dataset(df=parsed_df, adsh=APPLE_2024_10K_ADSH)
    cleaned_df.reset_index(inplace=True)

    cleaned_df = cleaned_df[~(cleaned_df.stmt=='CP')]

    return cleaned_df


@pytest.fixture
def num_parsed_df(sec_num_xml_parser) -> pd.DataFrame:

    content_num = read_content_from_zip(str(RAW_XML_PATH / '0000320193-24-000123-aapl-20240928_htm.xml'))

    parsed_df, _ = sec_num_xml_parser.parse(adsh=APPLE_2024_10K_ADSH, data=content_num)

    cleaned_df, fye = sec_num_xml_parser.clean_for_financial_statement_dataset(df=parsed_df, adsh=APPLE_2024_10K_ADSH)
    cleaned_df.reset_index(inplace=True)

    return cleaned_df


@pytest.fixture
def pre_orig_df() -> pd.DataFrame:
    dtypes = {
        'adsh': str,
        'stmt': str,
        'tag': str,
        'version': str,
        'line': int,
        'report': int,
        'negating': int,
        'plabel': str
    }
    df = read_file_from_zip(str(TESTDATA_PATH / '2024q4.zip'), 'pre.txt', dtype=dtypes)
    return df

@pytest.fixture
def num_orig_df() -> pd.DataFrame:
    dtypes = {
        'adsh': str,
        'tag': str,
        'version': str,
        'ddate': int64,
        'qtrs': int,
        'uom': str,
        'coreg': str,
        'value': float64,
        'footnote': str,
        'segments': str
    }
    df = read_file_from_zip(str(TESTDATA_PATH / '2024q4.zip'), 'num.txt', dtype=dtypes)
    df.loc[df.coreg.isnull(), 'coreg'] = ""
    df.loc[df.segments.isnull(), 'segments'] = ""
    df.loc[df.footnote.isnull(), 'footnote'] = ""

    df = df[df.segments == ""]
    return df


def load_from_raw_xml(base_path: Path, file_prefix: str) -> Tuple[pd.DataFrame, pd.DataFrame, List[SecError]]:
    num_file = str(base_path / f'{file_prefix}_htm.xml')
    pre_file = str(base_path / f'{file_prefix}_pre.xml')
    lab_file = str(base_path / f'{file_prefix}_lab.xml')

    adsh = "-".join(file_prefix.split('-')[0:3])

    return load_from_raw_xml_2(num_file, pre_file, lab_file, adsh)

def load_from_raw_xml_2(num_file: str, pre_file: str, lab_file: str, adsh) -> Tuple[pd.DataFrame, pd.DataFrame, List[SecError]]:

    numparser = SecNumXmlParser()
    preparser = SecPreXmlParser()
    labparser = SecLabXmlParser()

    content_num = read_content_from_zip(num_file)
    content_pre = read_content_from_zip(pre_file)
    content_lab = read_content_from_zip(lab_file)

    parsed_pre_df, errors_pre = preparser.parse(adsh=adsh, data=content_pre)
    parsed_num_df, errors_num = numparser.parse(adsh=adsh, data=content_num)
    parsed_lab_df, errors_lab = labparser.parse(adsh=adsh, data=content_lab)

    print("pre_errors: ", errors_pre)
    print("num_errors: ", errors_num)
    print("lab_errors: ", errors_lab)

    formatter = SECPreNumFormatter()

    pre_formatted_df, num_formatted_df, errorlist = formatter.format(adsh=adsh, pre_df=parsed_pre_df, num_df=parsed_num_df, lab_df=parsed_lab_df)

    print("pre shape: ", pre_formatted_df.shape)
    print("num shape: ", num_formatted_df.shape)
    print("errorlist: ", errorlist)

    return pre_formatted_df, num_formatted_df, errorlist

def compare_tables(df_orig: pd.DataFrame, df_daily: pd.DataFrame, cols: List[str], save_path: Optional[Path] = None):
    try:
        assert_frame_equal(df_daily, df_orig, check_dtype=True)
    except AssertionError:
        print("Differences in DataFrame")
        diff_pre = df_daily.merge(df_orig, indicator=True, how='outer')

        diff_pre = diff_pre.sort_values(cols)
        diff_pre = diff_pre[cols + ['_merge']]
        if save_path:
            diff_pre.to_parquet(save_path)
        else:print(diff_pre[diff_pre['_merge'] != 'both'])


def test_process(pre_orig_df, num_orig_df, print_full_table):
    adsh = "0001477932-24-008123"
    num_file = "d:/secprocessing2/xml/2025-03-17/0001477932-24-008123-upxi_10k_htm.xml"
    pre_file = "d:/secprocessing2/xml/2025-03-17/0001477932-24-008123-upxi-20240630_pre.xml"
    lab_file = "d:/secprocessing2/xml/2025-03-17/0001477932-24-008123-upxi-20240630_lab.xml"

    pre_df, num_df, _ = load_from_raw_xml_2(num_file, pre_file, lab_file, adsh)
    pre_orig_df = pre_orig_df[pre_orig_df.adsh == adsh]
    num_orig_df = num_orig_df[num_orig_df.adsh == adsh]

    # file_prefix = "0000320193-24-000123-aapl-20240928"
    # base_path = Path("D:/secprocessing2/xml/2025-03-17")
    # pre_df, num_df, _  =load_from_raw_xml(base_path=base_path, file_prefix=file_prefix)

    pre_df_cols = ['adsh', 'stmt', 'tag', 'version', 'negating', 'plabel'] # don't compare report and line
    num_df_cols = ['adsh', 'tag', 'version', 'ddate', 'qtrs', 'coreg', 'uom', 'value', 'segments', 'footnote']

    pre_df = pre_df[pre_df_cols]
    pre_orig_df = pre_orig_df[pre_df_cols]

    compare_tables(pre_orig_df, pre_df, pre_df_cols, save_path=SANDBOXDATA_PATH / f"diff_pre_{adsh}.parquet")
    compare_tables(num_orig_df, num_df, num_df_cols, save_path=SANDBOXDATA_PATH / f"diff_num_{adsh}.parquet")


def test_pre_single_compare(sec_pre_xml_parser: SecPreXmlParser, pre_parsed_df: pd.DataFrame):

    orig_df = pd.read_csv(TESTDATA_PATH / 'quarterzips' / '_2024_10k_apple' / 'pre.txt', sep='\t')

    cleaned_df = pre_parsed_df

    assert len(cleaned_df) > 0
    assert len(orig_df) == len(cleaned_df)



def test_num_single_compare(sec_num_xml_parser: SecNumXmlParser, num_parsed_df: pd.DataFrame):

    orig_df = pd.read_csv(TESTDATA_PATH / 'quarterzips' / '_2024_10k_apple' / 'num.txt', sep='\t')
    orig_df = orig_df[orig_df.segments.isnull()]

    cleaned_df = num_parsed_df

    assert len(orig_df) == len(cleaned_df)


    assert len(cleaned_df) > 0


def test_merge(pre_parsed_df: pd.DataFrame, num_parsed_df: pd.DataFrame, pre_orig_df: pd.DataFrame, num_orig_df: pd.DataFrame):
    common_columns = ['adsh', 'tag', 'version']
    merged_df = pd.merge(pre_parsed_df[common_columns], num_parsed_df[common_columns], on=common_columns, how='inner')

    pre_df = pre_parsed_df[pre_parsed_df[common_columns].apply(tuple, axis=1).isin(merged_df[common_columns].apply(tuple, axis=1))]
    num_df = num_parsed_df[num_parsed_df[common_columns].apply(tuple, axis=1).isin(merged_df[common_columns].apply(tuple, axis=1))]

    print("\nmerged len: ", len(merged_df))
    print("pre    len: ", len(pre_df))
    print("num    len: ", len(num_df))

    print("pre orig len: ", len(pre_orig_df))
    print("num orig len: ", len(num_orig_df))

    pre_df_cols = list(set(pre_df.columns) - set(['rfile', 'plabel']))

    pre_df_filtered = pre_df[pre_df_cols]
    pre_orig_df_filtered = pre_orig_df[pre_df_cols]

    pre_df_filtered = pre_df_filtered.sort_values(by=pre_df_cols).reset_index(drop=True)
    pre_orig_df_filtered = pre_orig_df_filtered.sort_values(by=pre_df_cols).reset_index(drop=True)

    assert len(merged_df) > 0
    try:
        assert_frame_equal(pre_df_filtered, pre_orig_df_filtered, check_dtype=False)
    except AssertionError:
        print("Differences in pre DataFrame:")
        diff_pre = pre_df_filtered.merge(pre_orig_df_filtered, indicator=True, how='outer')

        diff_pre = diff_pre.sort_values(['adsh', 'stmt', 'line', 'tag', 'version'])
        print(diff_pre[diff_pre['_merge'] != 'both'])

    # assert assert_frame_equal(num_df, num_orig_df, check_dtype=False)



