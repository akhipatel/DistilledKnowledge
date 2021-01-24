from bs4 import BeautifulSoup
import sqlite3
import urllib.request
import re


class EPI_Scraper:
    country_insert_stmt = '''INSERT INTO country VALUES (?, ?);'''
    country_insert_check = '''SELECT 1 FROM country WHERE ccode=?;'''
    epi_insert_stmt = '''INSERT INTO epi_score VALUES (?, ?, ?, ?, ?);'''
    epi_delete_stmt = '''DELETE FROM epi_score;'''
    country_delete_stmt = '''DELETE FROM country;'''
    
    epi_url = "https://epi.yale.edu/epi-indicator-report/H2O"
    table_class = "views-table sticky-enabled cols-5"
    ccode_regexp = "/epi-country-report/(.*)"
    
    batch_limit = 100

    def __init__(self, db):
        self.conn = db
        self.c = self.conn.cursor()
        self.epi_batch = []
        self.ccode_batch = []
        
        page = urllib.request.urlopen(EPI_Scraper.epi_url)
        self.soup = BeautifulSoup(page, 'html.parser')
        
        self.c.execute(EPI_Scraper.epi_delete_stmt)
        self.c.execute(EPI_Scraper.country_delete_stmt)
        self.conn.commit()
        
    def scrape(self):
        table = self.soup.find("tbody")
        table = table.select("tr")
        
        for tr in table:
            epi_atts = []
            columns = tr.select("td")
            
            ccode = self.save_ccode(columns.pop(0))
            epi_atts.append(ccode)
            
            is_float = 1
            for td in columns:
                next_val = td.get_text().strip("\n")
                if (is_float > 0):
                    next_val = int(next_val)
                    is_float *= -1
                else:
                    next_val = float(next_val)
                    is_float *= -1
                epi_atts.append(next_val)
                
            self.batch(self.epi_batch, epi_atts, EPI_Scraper.epi_insert_stmt)
            
        self.batch_insert(self.ccode_batch, EPI_Scraper.country_insert_stmt)
        self.batch_insert(self.epi_batch, EPI_Scraper.epi_insert_stmt)
                
            
    def save_ccode(self, td):
        link = td.select_one("a").get("href")
        ccode = re.search(EPI_Scraper.ccode_regexp, link).groups(0)[0]
        country_name = td.get_text().strip()
        
        q_args = [ccode, country_name]
        self.c.execute(EPI_Scraper.country_insert_check, (ccode,))
        if (self.c.fetchone() == None):
            self.batch(self.ccode_batch, q_args, EPI_Scraper.country_insert_stmt)
        
        return ccode
        
    def batch(self, batch, data, query):
        batch.append(data)
        
        if (len(batch) == EPI_Scraper.batch_limit):
            self.batch_insert(batch, query)
     
    def batch_insert(self, batch, query):
        if (len(batch) > 0):
            self.c.executemany(query, batch)
            self.conn.commit()
            batch.clear()
        
if __name__ == "__main__":
    scraper = EPI_Scraper("wq_test.db")
    scraper.scrape()
    scraper.close() 