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
def download_index_files(history , backwards = True):
	urls = ['https://www.sec.gov/Archives/edgar/full-index/%d/%s/crawler.idx' % (x[0], x[1]) for x in history]
	urls.sort()

	if backwards:
		urls = urls[::-1] # download backwards

	crawlerfolder = "Downloaded index files"
	create_folder(crawlerfolder)

	paths = []
	for url,hist in zip(urls,history):
		year = hist[0]
		quarter = hist[1]
		request = requests.get(url,timeout = 10)
		filename = str(year)+'-'+str(quarter)
		path = crawlerfolder + '/' + filename+ '.txt'
		with open(path, 'wb') as fd:
			    [fd.write(chunk) for chunk in request.iter_content(chunk_size=20480)]
			    paths.append(path)
	return paths

def all_txt_to_csv(crawlerfolder,database_folder,paths):
	create_folder(database_folder)

	paths = sorted([ (os.path.join(crawlerfolder, filename)) for filename in paths if filename.endswith('.txt')])
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

def get_year_quarters(begin,end):
	years = list(range(begin, end))
	quarters = ['QTR1', 'QTR2', 'QTR3', 'QTR4']
	history = [(y, q) for y in years for q in quarters]
	if end == datetime.date.today().year:
		current_quarter = (datetime.date.today().month - 1) // 3 + 1
		for i in range(1, current_quarter + 1):
		    history.append((end, 'QTR%d' % i))
		history = history[:-1] # not including the current quarter, since not updated on SEC anyway
	return history

def check_csvs(history, database_folder):

	if not os.path.exists(database_folder):
		return history
	else:
		downloaded_csvs = sorted([ csv for csv in os.listdir(database_folder) if csv.endswith('.csv')])
		history = [hist for hist in history if "{}-{}.csv".format(str(hist[0]),hist[1]) not in downloaded_csvs ]
		return history

def prepare_database(begin=2017,end=None):
	if begin < 1993:
		begin = 1993
		print("SEC has data as early as 1993.")
	if end is None:
		end = datetime.date.today().year
		print("Current year {} is used as the end of period for data preparation.".format(str(end)))
	
	history = get_year_quarters(begin,end)
	database_folder = "Database files"
	history = check_csvs(history,database_folder)
	downloaded_txts =  download_index_files(history)
	crawlerfolder = "Downloaded index files"
	all_txt_to_csv(crawlerfolder,database_folder,downloaded_txts)
	return database_folder
