import os
import shutil

import pandas as pd
import pytest

import secdaily._00_common.SecFileUtils as sfu

folder = "./tmp/"


@pytest.fixture(scope="module")
def wrap():
    shutil.rmtree(folder, ignore_errors=True)
    os.makedirs(folder)
    yield ""
    shutil.rmtree(folder)


def test_write_read_content_to_zip(wrap: str):
    filename = folder + "mycontent.txt"
    writecontent = "some content"
    sfu.write_content_to_zip("some content", filename)
    readcontent = sfu.read_content_from_zip(filename)

    assert os.path.isfile(filename + ".zip")
    assert writecontent == readcontent


def test_write_read_df_to_zip(wrap: str):
    filename = folder + "acsv.csv"
    d = {'col1': [1, 2], 'col2': [3, 4]}
    df = pd.DataFrame(data=d)

    sfu.write_df_to_zip(df, filename)
    readdf = sfu.read_df_from_zip(filename)
    readdf.set_index("Unnamed: 0", inplace=True)

    assert os.path.isfile(filename + ".zip")
    assert df.equals(readdf)
