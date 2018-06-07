import os,datetime
from selenium import webdriver
import time,requests,errno
from re import search
import sqlite3
import requests
import time


# Generate the list of index files archived in EDGAR since start_year (earliest: 1993) until the most recent quarter

def download_index_files(year=2016,backwards = True):
	current_year = datetime.date.today().year
	current_quarter = (datetime.date.today().month - 1) // 3 + 1

	start_year = year # choose the year to start
	years = list(range(start_year, current_year))
	quarters = ['QTR1', 'QTR2', 'QTR3', 'QTR4']
	history = [(y, q) for y in years for q in quarters]
	for i in range(1, current_quarter + 1):
	    history.append((current_year, 'QTR%d' % i))
	urls = ['https://www.sec.gov/Archives/edgar/full-index/%d/%s/crawler.idx' % (x[0], x[1]) for x in history]
	urls.sort()
	if backwards:
		urls = urls[::-1] # download backwards

	print("Year {} to current date is seleted.".format(str(start_year)))
	# print("You have a total of {} quarters of filing indices to download.".format(len(urls)))


	crawlerfolder = "Downloaded index files"
	try:
	    os.makedirs(crawlerfolder)
	except OSError as e:
	    if e.errno != errno.EEXIST:
	        raise

	for url,hist in zip(urls,history):
		year = hist[0]
		quarter = hist[1]
		# print("Downloading from : =>   "+ url)
		request = requests.get(url,timeout = 10)
		filename = str(year)+'-'+str(quarter)
		path = crawlerfolder + '/' + filename+ '.txt'
		with open(path, 'wb') as fd:
			    [fd.write(chunk) for chunk in request.iter_content(chunk_size=20480)]
		# print('\n'+url, 'downloaded and wrote to txt')
	return crawlerfolder

def convert_txt_csv(crawlerfolder):

	# crawlerfolder = "Downloaded index files"
	paths = sorted([ (os.path.join(crawlerfolder, filename)) for filename in os.listdir(crawlerfolder) if filename.endswith('.txt')])

	period = "{} to {}".format((search('\d{4}-QTR\d{1}', paths[0]).group(0)),(search('\d{4}-QTR\d{1}', paths[-1]).group(0)))
	database = period + '.db'

	con = sqlite3.connect(database)
	cur = con.cursor()
	cur.execute('DROP TABLE IF EXISTS idx')
	cur.execute('CREATE TABLE idx (conm TEXT, type TEXT, cik TEXT, date TEXT, path TEXT, download INT)')


	for path in paths:
	    # print("Converting to data base index from ===>  "+ path )
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
	        # print(path, 'converted text index and wrote to SQLite')

	con.commit()
	con.close()

	# Write SQLite database to csv
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
	    database = database_folder+ '/' +period+'.csv'
	    data.to_csv(database,index=False)
	return database

def download_and_convert(year=2017):
	database = convert_txt_csv(download_index_files(year=year))
	# print("Successfully downloaded all index files and stored as csv.")
	return database
