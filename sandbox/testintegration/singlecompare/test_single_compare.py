import pytest
from pathlib import Path

import pandas as pd

from secdaily._00_common.SecFileUtils import read_content_from_zip
from secdaily._02_xml.parsing.SecXmlNumParsing import SecNumXmlParser
from secdaily._02_xml.parsing.SecXmlPreParsing import SecPreXmlParser

CURRENT_PATH = Path(__file__).parent
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
    df = pd.read_csv(TESTDATA_PATH / 'quarterzips' / '_2024_10k_apple' / 'pre.txt', sep='\t')
    return df

@pytest.fixture
def num_orig_df() -> pd.DataFrame:
    df = pd.read_csv(TESTDATA_PATH / 'quarterzips' / '_2024_10k_apple' / 'num.txt', sep='\t')
    df = df[df.segments.isnull()] 
    return df


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


    assert len(merged_df) > 0



