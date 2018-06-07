# Download index files and write content into SQLite
import sqlite3
import requests
import time
import os
import IndexDownloader
import errno


# IndexDownloader.download_index_files(2008)
crawlerfolder = "Downloaded index files"
paths = sorted([ (os.path.join(crawlerfolder, filename)) for filename in os.listdir(crawlerfolder) if filename.endswith('.txt')])

period = "{} to {}".format((search('\d{4}-QTR\d{1}', paths[0]).group()),(search('\d{4}-QTR\d{1}', paths[-1]).group()))
database = period + '.db'

con = sqlite3.connect(database)
cur = con.cursor()
cur.execute('DROP TABLE IF EXISTS idx')
cur.execute('CREATE TABLE idx (conm TEXT, type TEXT, cik TEXT, date TEXT, path TEXT, download INT)')

for path in paths:
    print("Converting to data base index from ===>  "+ path )
    with open(path,'r',encoding="latin1") as infile: 

        lines = infile.readlines()

        nameloc = lines[7].find('Company Name')
        typeloc = lines[7].find('Form Type')
        cikloc = lines[7].find('CIK')
        dateloc = lines[7].find('Date Filed')
        urlloc = lines[7].find('URL')
        records = [  tuple([line[:typeloc].strip(), line[typeloc:cikloc].strip(), line[cikloc:dateloc].strip(),
                          line[dateloc:urlloc].strip(), line[urlloc:].strip(), 0]) for line in lines[9:]]
        cur.executemany('INSERT INTO idx VALUES (?, ?, ?, ?, ?,?)', records)
        print(path, 'converted text index and wrote to SQLite')

con.commit()
con.close()

# Write SQLite database to Stata
import pandas
from sqlalchemy import create_engine

database_folder = "Database files"
try:
    os.makedirs(database_folder)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

engine = create_engine('sqlite:///'+database)
with engine.connect() as conn, conn.begin():
    data = pandas.read_sql_table('idx', conn)
    data.to_csv(database_folder+ '/' +period+'.csv',index=False)
