from _02_xml.parsing.num._2_SecNumXmlTransformation import SecNumXmlTransformer

import os

scriptpath = os.path.realpath(__file__ + "/../..")
datafolder = scriptpath + "/data/"


def test_find_last_day_of_month():
    parser = SecNumXmlTransformer()

    assert parser._find_close_last_day_of_month("2019-11-25") == "20191130"
    assert parser._find_close_last_day_of_month("2019-02-05") == "20190131"
    assert parser._find_close_last_day_of_month("2020-02-05") == "20200131"
    assert parser._find_close_last_day_of_month("2020-02-20") == "20200229"
    assert parser._find_close_last_day_of_month("2019-12-25") == "20191231"
    assert parser._find_close_last_day_of_month("2021-01-15") == "20201231"
    assert parser._find_close_last_day_of_month("2021-02-15") == "20210131"


def test_calculate_qtrs():
    parser = SecNumXmlTransformer()

    assert parser._calculate_qtrs("19", "09", "01", "20", "09", "01") == 4
    assert parser._calculate_qtrs("19", "06", "01", "19", "09", "01") == 1
    assert parser._calculate_qtrs("19", "10", "01", "20", "09", "01") == 4
    assert parser._calculate_qtrs("19", "08", "01", "19", "10", "01") == 1
