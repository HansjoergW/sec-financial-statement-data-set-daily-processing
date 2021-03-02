from _00_common import indexer as ix
work_dir = 'd:/edgar'
from_year = 2021
to_year = 2021

if __name__ == '__main__':
    indexer = ix.SecIndexer(work_dir)
    #indexer.download_sec_feeds(from_year, to_year, from_month=1, to_month=2)
    indexer._find_missing_urls()


#cik = ix.get_cik('AAPL')
#indexer.download_xbrl_data(cik, from_year, to_year, 'All')

# indexer.download_xbrl_data("0001441082", from_year, to_year, 'All')

# es gibt in jedem Verzeichnis ein index.json
# https://www.sec.gov/Archives/edgar/data/861459/000143774921004124/index.json
# darin kann man über die Liste mit den vorhanden Files suchen
# wenn das xbrl. data file nicht vorhanden ist, wird in der Regel eines geeneriert, das endet mit dem Namen *htm.xml
