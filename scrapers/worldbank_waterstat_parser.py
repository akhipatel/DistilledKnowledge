import csv
import sqlite3
import re


class WB_CSV_Parser:
    field_dict = {
        "cname" : "Country Name",
        "ccode" : "Country Code",
        "sname" : "Series Name",
        "scode" : "Series Code"
    }
    year_regexp = "([0-9]{4}) \[YR([0-9]{4})\]"
    
    country_check_stmt = "SELECT 1 FROM country WHERE ccode=?;"
    series_check_stmt = "SELECT 1 FROM wb_series WHERE scode=?;"
    
    country_insert_stmt = "INSERT INTO country VALUES (?,?);"
    series_insert_stmt = "INSERT INTO wb_series VALUES (?,?);"
    series_data_insert_stmt = "INSERT INTO wb_series_data VALUES (?,?,?,?);"
    
    series_delete_stmt = "DELETE FROM wb_series;"
    series_data_delete_stmt = "DELETE FROM wb_series_data;"
    
    batch_limit = 100

    def __init__(self, db, csv_filename):
        self.conn = db
        self.c = self.conn.cursor()
        
        self.csv_file = open(csv_filename, 'r')
        self.csv_reader = csv.reader(self.csv_file)
        self.years = []
        
        self.country_batch = []
        self.wb_series_batch = []
        self.wb_series_data_batch = []
        
        self.c.execute(WB_CSV_Parser.series_data_delete_stmt)
        self.c.execute(WB_CSV_Parser.series_delete_stmt)
        self.conn.commit()
        
    def parse(self):
        fields = next(self.csv_reader)
        self.parse_year_fields(fields[4:])
    
        for row in self.csv_reader:
            country_name = row[0]
            ccode = row[1]
            series_name = row[2]
            scode = row[3]
    
            self.save_code_and_name(ccode, country_name, self.country_batch, WB_CSV_Parser.country_check_stmt)
            self.save_code_and_name(scode, series_name, self.wb_series_batch, WB_CSV_Parser.series_check_stmt)
            
            for i in range(len(self.years)):
                year_val = row[i + 4]
                if (year_val == ".."):
                    year_val = None
                else:
                    year_val = float(year_val)
                    
                year = self.years[i]
                series_data = [scode, ccode, year, year_val]
                self.batch(self.wb_series_data_batch, series_data)
                
        self.batch_insert_all()
    
    def parse_year_fields(self, year_fields):
        for yf in year_fields:
            year = re.search(WB_CSV_Parser.year_regexp, yf).groups(0)[0]
            self.years.append(int(year))
            
    def save_code_and_name(self, code, name, batch, query):
        data = [code, name]
        self.c.execute(query, (code,))
        if (self.c.fetchone() == None and data not in batch):
            self.batch(batch, data)
            
    def batch(self, batch, data):
        batch.append(data)
        if (len(batch) == WB_CSV_Parser.batch_limit):
            self.batch_insert_all()
    
    def batch_insert_all(self):
        self.batch_insert(self.country_batch, self.country_insert_stmt)
        self.batch_insert(self.wb_series_batch, self.series_insert_stmt)
        self.batch_insert(self.wb_series_data_batch, self.series_data_insert_stmt)
        
    def batch_insert(self, batch, query):
        self.c.executemany(query, batch)
        self.conn.commit()
        batch.clear()
    
    def close(self):
        self.csv_file.close()