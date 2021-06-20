import _00_common.SecFileUtils as sfu
import pytest
import shutil
import os

folder = "./tmp/"

@pytest.fixture(scope="module")
def wrap():
    shutil.rmtree(folder, ignore_errors=True)
    os.makedirs(folder)
    yield ""
    shutil.rmtree(folder)

def test_write_read_content_to_zip(wrap:str):
    filename = folder + "mycontent.txt"
    writecontent = "some content"
    sfu.write_content_to_zip("some content", filename)
    readcontent = sfu.read_content_from_zip(filename)

    assert writecontent == readcontent
