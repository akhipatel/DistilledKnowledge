import sqlite3

def main():
    conn = sqlite3.connect("wq_test.db")
    create_stmts = open("create_tables.sql", 'r').read()
    
    c = conn.cursor()
    c.executescript(create_stmts)
    conn.commit();
    
    conn.close();

if __name__ == "__main__":
    main()