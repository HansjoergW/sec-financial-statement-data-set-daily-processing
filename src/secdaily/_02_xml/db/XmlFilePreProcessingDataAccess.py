import pandas as pd

from secdaily._00_common.DBBase import DB


class XmlFilePreProcessingDA(DB):

    # copies entries from the feed table to the processing table if they are not already present
    def copy_uncopied_entries(self) -> int:
        sql = f"""SELECT accessionNumber, cikNumber, filingDate, formType,
                         xbrlInsUrl, insSize, xbrlPreUrl, preSize, xbrlLabUrl, labSize
                  FROM {DB.SEC_REPORTS_TBL_NAME}
                  WHERE status is null and xbrlInsUrl is not null"""
        to_copy_df = self._execute_read_as_df(sql)

        to_copy_df["filingMonth"] = pd.to_numeric(to_copy_df.filingDate.str.slice(0, 2), downcast="integer")
        to_copy_df["filingDay"] = pd.to_numeric(to_copy_df.filingDate.str.slice(3, 5), downcast="integer")
        to_copy_df["filingYear"] = pd.to_numeric(to_copy_df.filingDate.str.slice(6, 10), downcast="integer")

        conn = self.get_connection()
        try:
            to_copy_df.to_sql(DB.SEC_REPORT_PROCESSING_TBL_NAME, conn, index=False, if_exists="append", chunksize=1000)

            update_sql = f"""UPDATE {DB.SEC_REPORTS_TBL_NAME} SET status = 'copied'
                             WHERE accessionNumber = ? and status is null """
            adshs = to_copy_df.accessionNumber.values.tolist()
            tupleslist = [tuple(x.split()) for x in adshs]

            conn.executemany(update_sql, tupleslist)

            conn.commit()
            return len(to_copy_df)
        finally:
            conn.close()
