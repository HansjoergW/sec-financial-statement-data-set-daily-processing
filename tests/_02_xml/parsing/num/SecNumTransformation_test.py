from secdaily._02_xml.parsing.num._2_SecNumXmlTransformation import SecNumXmlTransformer

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

    assert parser._calculate_qtrs("2019", "09", "01", "2020", "09", "01") == 4
    assert parser._calculate_qtrs("2019", "06", "01", "2019", "09", "01") == 1
    assert parser._calculate_qtrs("2019", "10", "01", "2020", "09", "01") == 4
    assert parser._calculate_qtrs("2019", "08", "01", "2019", "10", "01") == 1
    assert parser._calculate_qtrs("1980", "01", "01", "2020", "12", "31") == 164
    assert parser._calculate_qtrs("2008", "03", "31", "2021", "01", "31") == 51
    assert parser._calculate_qtrs("2012", "02", "25", "2020", "12", "31") == 35


def test_clean_member():
    parser = SecNumXmlTransformer()

    assert parser._clean_member_domain_from_coreg("xyMember") == "xy"
    assert parser._clean_member_domain_from_coreg("xyDomain") == "xy"
    assert parser._clean_member_domain_from_coreg("xyMemberDomain") == "xyMember"
    assert parser._clean_member_domain_from_coreg("xyMemberab") == "xyMemberab"
    assert parser._clean_member_domain_from_coreg("xyDomainab") == "xyDomainab"
    assert parser._clean_member_domain_from_coreg("xyMemberDomainab") == "xyMemberDomainab"
    assert parser._clean_member_domain_from_coreg("xyMemberMember") == "xyMember"
    assert parser._clean_member_domain_from_coreg("xyDomainDomain") == "xyDomain"


