from epi_scraper import EPI_Scraper
from gobi_scraper import GOBI_Scraper
from worldbank_waterstat_parser import WB_CSV_Parser
import sqlite3
import sys


def main():
    if (len(sys.argv) == 3):
        db_name = sys.argv[1]
        csv_filename = sys.argv[2]
    else:
        db_name = "water_quality.db"
        csv_filename = "wbseries_data.csv"

    db = sqlite3.connect(db_name)
    c = db.cursor()
    create_stmts = open("create_tables.sql", 'r').read()
    
    try:
        c.executescript(create_stmts)
    except:
        pass
    
    epi = EPI_Scraper(db)
    epi.scrape()
    
    gobi = GOBI_Scraper(db)
    gobi.scrape()
    
    wb_series = WB_CSV_Parser(db, csv_filename)
    wb_series.parse()
    wb_series.close()
    
    db.close()

if __name__ == "__main__":
    main()