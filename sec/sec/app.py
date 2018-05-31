# Generate the list of index files archived in EDGAR since start_year (earliest: 1993) until the most recent quarter

# (download crawler urls into a stata database)
print("PART 1: This part downloads crawler urls into a stata database named: 'edgar_htm_idx.db' ")
print()
import datetime

current_year = datetime.date.today().year
current_quarter = (datetime.date.today().month - 1) // 3 + 1


start_year = 2018 # choose the year to start


years = list(range(start_year, current_year))
quarters = ['QTR1', 'QTR2', 'QTR3', 'QTR4']
history = [(y, q) for y in years for q in quarters]
for i in range(1, current_quarter + 1):
    history.append((current_year, 'QTR%d' % i))
urls = ['https://www.sec.gov/Archives/edgar/full-index/%d/%s/crawler.idx' % (x[0], x[1]) for x in history]
urls.sort()

print("Year {} to current date is seleted. All {} quarters are used".format(str(start_year),len(quarters)))
print()
# Download index files and write content into SQLite
import sqlite3
import requests

con = sqlite3.connect('edgar_htm_idx.db')
cur = con.cursor()
cur.execute('DROP TABLE IF EXISTS idx')
cur.execute('CREATE TABLE idx (conm TEXT, type TEXT, cik TEXT, date TEXT, path TEXT)')

for url in urls:
    print("Downloading from : =>      "+ url)
    lines = requests.get(url).text.splitlines()
    nameloc = lines[7].find('Company Name')
    typeloc = lines[7].find('Form Type')
    cikloc = lines[7].find('CIK')
    dateloc = lines[7].find('Date Filed')
    urlloc = lines[7].find('URL')
    records = [tuple([line[:typeloc].strip(), line[typeloc:cikloc].strip(), line[cikloc:dateloc].strip(),
                      line[dateloc:urlloc].strip(), line[urlloc:].strip()]) for line in lines[9:]]
    cur.executemany('INSERT INTO idx VALUES (?, ?, ?, ?, ?)', records)
    print(url, 'downloaded and wrote to SQLite')

con.commit()
con.close()

# Write SQLite database to Stata
import pandas
from sqlalchemy import create_engine

engine = create_engine('sqlite:///edgar_htm_idx.db')
with engine.connect() as conn, conn.begin():
    data = pandas.read_sql_table('idx', conn)
    data.to_stata('edgar_htm_idx.dta')


# output the queried filings to a query.csv
print("*************************************************************************")
print("PART 2: This part outputs the queried filings to a csv named 'query.csv' ")
print()
print()
import pandas as pd

database_name = "edgar_htm_idx.dta"
database = pd.read_stata(database_name)
print("There are a total of {} entries of filing links".format(str(len(database))))
print("Note: these are not document links, but filing links.")

# dropping the useless 'index' column
database.drop(columns = ['index'],inplace=True)
def select_queries(user_requests):
    # to be implemented
    return 

# output what you want to query.csv

print("Try 5 first before the entire database")
print("Depending on the conditions, downloading 1 filing can take up to 30 seconds")



database.head(5).to_csv("query.csv")  # choose how many to download



# uncomment this line below to create a csv that queries the entire database downloaded
# database.to_csv("query.csv") 


# download all the files for each filing in the query.csv
print("*************************************************************************")
print("PART 3: This part downloads all the files for each filing in the query.csv to a folder named: 'Downloaded data files' ,")
print("PART 3: Docments for each filing is downloaded to its respectively created subfolder.")
print()
print()

import urllib,csv,random
import os, errno,  wget
import time
from selenium import webdriver

datafolder = "Downloaded data files"
try:
    os.makedirs(datafolder)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

with open('log.csv', 'w', newline='') as log:
    logwriter = csv.writer(log)

    with open('query.csv', newline='') as infile:

        has_header = csv.Sniffer().has_header(infile.read(1024))
        infile.seek(0)  # Rewind.
        records = csv.reader(infile)
        if has_header:
            next(records)  # Skip header row.

        for r in records:
            log_row = r.copy()
            print('Start fetching URL to', r[2], r[3], 'filed on', r[4], '...')
            start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

            driver = webdriver.Chrome('./chromedriver_win32/chromedriver.exe')
            # driver = webdriver.Chrome(os.path.join(os.getcwd(), 'chromedriver'))  # this is for mac users

            try:
                driver.get(r[5])
                foldername = r[2]+"-"+r[3]+"-"+r[4] # use * for convenient coding separation
                path = datafolder+ '/' + foldername
                try:
                    os.makedirs(path)
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        raise
                
                with open(path+'/'+'download.log', 'w', newline='') as download_log:
                    
                    download_log.write("Filing url is: " +" "+r[5]+"\n")
                    download_log.write("\n")

                    # print(len(driver.find_elements_by_xpath('.//a')))
                    for a in driver.find_elements_by_xpath('.//a'):
                        url = a.get_attribute('href')    # print(a.get_attribute('href'))
                        PREFIX = "https://www.sec.gov/Archives/edgar/data/" # common prefix for data files

                        if(url.startswith(PREFIX)):
                            filename = url.split('/')[-1]
                            wget.download(url , path + '/'+ filename)
                            download_log.write("filename is : " + filename +"\n")
                            download_log.write("link is : "+ url + "\n")


                time.sleep(3 + random.random() * 3)
                filing_date = driver.find_element_by_xpath('//*[@id="formDiv"]/div[2]/div[1]/div[2]').text
                period_of_report = driver.find_element_by_xpath('//*[@id="formDiv"]/div[2]/div[2]/div[2]').text
                form_text = driver.find_element_by_xpath('//*[@id="formDiv"]/div/table/tbody/tr[2]/td[3]/a').text
                form_link = driver.find_element_by_link_text(form_text).get_attribute('href')
                end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                print('Success!', start_time, ' --> ', end_time, '\n')
                log_row = log_row + [start_time, end_time, filing_date, period_of_report, form_link]

            except:
                end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                print('Error!', start_time, ' --> ', end_time, '\n')
                log_row = log_row + [start_time, end_time, 'ERROR!']
            driver.quit()

            logwriter.writerow(log_row)


print("All downloading complete.\n")