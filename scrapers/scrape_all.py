from epi_scraper import EPI_Scraper
from gobi_scraper import GOBI_Scraper
import sqlite3
import sys


def main():
    if (len(sys.argv) == 2):
        db_name = sys.argv[1]
    else:
        db_name = "water_quality.db"

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
    
    db.close()

if __name__ == "__main__":
    main()