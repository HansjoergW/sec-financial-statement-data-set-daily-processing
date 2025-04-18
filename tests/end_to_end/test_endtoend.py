from pathlib import Path
from typing import List, Tuple

import pandas as pd
from secdaily._00_common.ProcessBase import ErrorEntry
from secdaily._00_common.SecFileUtils import read_content_from_zip
from secdaily._02_xml.parsing.SecXmlLabParsing import SecLabXmlParser
from secdaily._02_xml.parsing.SecXmlNumParsing import SecNumXmlParser
from secdaily._02_xml.parsing.SecXmlPreParsing import SecPreXmlParser
from secdaily._03_secstyle.formatting.SECPreNumFormatting import SECPreNumFormatter

CURRENT_PATH = Path(__file__).parent


def process_from_raw_xml(path: Path) -> Tuple[pd.DataFrame, pd.DataFrame, List[ErrorEntry]]:
    adsh = path.name
    num_file = str(next(path.glob("*htm.xml.zip")))
    pre_file = str(next(path.glob("*pre.xml.zip")))
    lab_file = str(next(path.glob("*lab.xml.zip")))

    numparser = SecNumXmlParser()
    preparser = SecPreXmlParser()
    labparser = SecLabXmlParser()

    content_num = read_content_from_zip(num_file.replace(".zip", ""))
    content_pre = read_content_from_zip(pre_file.replace(".zip", ""))
    content_lab = read_content_from_zip(lab_file.replace(".zip", ""))

    parsed_pre_df, errors_pre = preparser.parse(adsh=adsh, data=content_pre)
    parsed_num_df, errors_num = numparser.parse(adsh=adsh, data=content_num)
    parsed_lab_df, errors_lab = labparser.parse(adsh=adsh, data=content_lab)

    print("pre_errors: ", errors_pre)
    print("num_errors: ", errors_num)
    print("lab_errors: ", errors_lab)

    formatter = SECPreNumFormatter()

    pre_formatted_df, num_formatted_df, errorlist = formatter.format(
        adsh=adsh, pre_df=parsed_pre_df, num_df=parsed_num_df, lab_df=parsed_lab_df
    )

    print("pre shape: ", pre_formatted_df.shape)
    print("num shape: ", num_formatted_df.shape)
    print("errorlist: ", errorlist)

    return pre_formatted_df, num_formatted_df, errorlist


def run_endtoend(path: Path):
    pre_df, num_df, errorlist = process_from_raw_xml(path)

    assert len(pre_df) > 0
    assert len(num_df) > 0
    assert len(errorlist) == 0

    # Read the pre.parquet file and compare it to the pre_df
    pre_parquet_df = pd.read_parquet(path / "pre.parquet")
    pd.testing.assert_frame_equal(pre_df, pre_parquet_df, check_dtype=False)

    # Read the num.parquet file and compare it to the num_df
    num_parquet_df = pd.read_parquet(path / "num.parquet")
    pd.testing.assert_frame_equal(num_df, num_parquet_df, check_dtype=False)


def test_apple_10k_2024():
    # default case
    path = CURRENT_PATH / "data" / "0000320193-24-000123"
    run_endtoend(path)


def test_upxi_2024():
    # case with direct plabel values
    path = CURRENT_PATH / "data" / "0001477932-24-008123"
    run_endtoend(path)
