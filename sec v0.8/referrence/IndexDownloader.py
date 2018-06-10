import os,datetime
from selenium import webdriver
import time,requests,errno
from re import search
import sqlite3
import requests
import time
import pandas as pd


def create_folder(folder_name):
	try:
		os.makedirs(folder_name)
	except OSError as e:
		if e.errno != errno.EEXIST:
			raise
	return

# Generate the list of index files archived in EDGAR since start_year (earliest: 1993) until the most recent quarter

def download_index_files(year=2016, backwards = True):
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
	urls = urls[:-1] # leave out the current quarter
	if backwards:
		urls = urls[::-1] # download backwards

	print("Year {} to current date is seleted.".format(str(start_year)))
	# print("You have a total of {} quarters of filing indices to download.".format(len(urls)))

	crawlerfolder = "Downloaded index files"
	create_folder(crawlerfolder)

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

def all_txt_to_csv(crawlerfolder,database_folder):
	
	paths = sorted([ (os.path.join(crawlerfolder, filename)) for filename in os.listdir(crawlerfolder) if filename.endswith('.txt')])
	startIndex = 0
	for path in paths:
		targetPath = path.replace(crawlerfolder,database_folder)[:-4]+".csv"
		startIndex = create_csv(path,targetPath,startIndex)
	return 

def create_csv(path,targetPath,startIndex):
	columns = ['index','comn','filing','cik','date','htm','download']
	data = []
	with open(path,'r',encoding = 'latin1' ) as file:
		for index,line in enumerate(file):  # index is 0-based and content starts from index == 9
			if( index < 9 ):
				continue
			comn = line[:62].strip()
			filing = line[62:72].strip()
			cik = line[72:83].strip()
			date = line[83:96].strip()
			htm = line[96:].strip()
			row = (index + startIndex - 8 ,comn,filing,cik,date,htm, 0)   # 1-indexed counting for files
																		# 0 to indicate download status: unfinished
			data.append(row)
	pd.DataFrame(data=data,columns=columns).to_csv(targetPath,index=False)
	return startIndex + len(data)


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
	database_folder = "Database files"
	create_folder(database_folder)
	all_txt_to_csv(download_index_files(year=year),database_folder)
	# database = convert_txt_csv(download_index_files(year=year))
	return database_folder

# download_and_convert(2017)