from _00_common.DBManagement import DBManager
from _00_common.DebugUtils import DataAccessTool, TestSetCreatorTool

from testintegration.sub.SubMassTestingTools import read_sub_zip_content, read_sub_xml_content

default_workdir = "d:/secprocessing"

dbmgr = DBManager(work_dir=default_workdir)
dataUtils = DataAccessTool(default_workdir)
testsetCreator = TestSetCreatorTool(default_workdir)

cols = ['adsh', 'cik', 'name', 'sic', 'fye', 'form', 'period', 'filed', 'accepted', 'fy', 'fp']

sub_zip_df = read_sub_zip_content(dbmgr, dataUtils, 2021, 1)[cols]
sub_xml_df = read_sub_xml_content(dbmgr, testsetCreator, 2021, 1)

#format sic, fye, period, acceppted, fy nicht identisch



print(len(sub_zip_df))
print(len(sub_xml_df))
print(sub_xml_df.columns)