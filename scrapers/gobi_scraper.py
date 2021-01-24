from bs4 import BeautifulSoup
import sqlite3
from urllib.request import Request, urlopen
import re


class GOBI_Scraper:
    batch_limit = 100
    
    gobi_url = "https://index.okfn.org/dataset/water/"
    country_check_stmt = "SELECT ccode FROM country WHERE name=?;"
    country_insert_stmt = "INSERT INTO country VALUES(?, ?);"
    gobi_insert_stmt = "INSERT INTO gobi_score VALUES (?,?,?,?,?,?,?,?);"
    gobi_delete_stmt = "DELETE FROM gobi_score;"
    
    criteria_dict = {
        "Openly licenced" : 0,
        "In an open and machine-readable format" : 0,
        "Downloadable at once" : 0,
        "Up-to-date" : 0,
        "Publicly available" : 0,
        "Available free of charge" : 0
    }
    
    def __init__(self, db):
        self.conn = db
        self.c = db.cursor()
        self.ccode_batch = []
        self.gobi_batch = []
        
        self.c.execute(GOBI_Scraper.gobi_delete_stmt)
        self.conn.commit()
        
        req = Request(GOBI_Scraper.gobi_url, headers={'User-Agent': 'Mozilla/5.0'})
        page = urlopen(req)
        self.soup = BeautifulSoup(page, 'html.parser')
        
    def scrape(self):
        table = self.soup.find("tbody")
        table = table.select("tr")
        
        for tr in table:
            gobi_atts = []
            all_td = tr.select("td")[1:]
            
            ccode = self.save_ccode(all_td.pop(0))
            score = all_td.pop(1).get_text().strip("\n")
            score = re.search("(.*)%", score).groups()[0]
            gobi_atts.append(ccode)
            gobi_atts.append(int(score))
            
            criteria = self.gather_criteria(all_td[0])
            gobi_atts += criteria
            self.batch(self.gobi_batch, gobi_atts, GOBI_Scraper.gobi_insert_stmt)
            
        self.batch_insert(self.ccode_batch, GOBI_Scraper.country_insert_stmt)
        self.batch_insert(self.gobi_batch, GOBI_Scraper.gobi_insert_stmt)
         
    def save_ccode(self, td):
        country_name = td.get_text().strip()
        self.c.execute(GOBI_Scraper.country_check_stmt, (country_name,))
        
        row = self.c.fetchone()
        if (row == None):
            ccode_url = td.find('a').get("href")
            ccode = re.search("/place/(.*)", ccode_url).groups(0)[0].strip("\n")
            self.batch(self.ccode_batch, [ccode, country_name], GOBI_Scraper.country_insert_stmt)
        else:
            ccode = row[0]
            
        return ccode
         
    def gather_criteria(self, td):
        all_criteria_tags = td.select("li")
        criteria = []
        
        for cr in all_criteria_tags:
            has_criteria = cr.get("class")[0]
            if (has_criteria == "yes"):
                criteria.append(1)
            else:
                criteria.append(0)
        
        return criteria
            
    def batch(self, batch, data, query):
        batch.append(data)
        if (len(batch) == GOBI_Scraper.batch_limit):
            self.batch_insert(batch)
    
    def batch_insert(self, batch, query):
        if (len(batch) > 0):
            self.c.executemany(query, batch)
            self.conn.commit()
            batch.clear()