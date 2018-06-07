import random,time,itertools,threading,re,datetime
import urllib,csv,os, errno, wget
from re import search
from urllib.parse import quote,unquote
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool 
from multiprocessing import Process
import shutil
import IndexDownloader
import numpy as np
from math import ceil
import pandas as pd 


def configure_web_driver():
	# to configure the webdriver 
	executable_path = os.path.join(os.getcwd(), 'chromedriver') 
	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_argument('--no-sandbox')
	chrome_options.add_argument('--headless')
	chrome_options.add_argument('--disable-gpu')
	# a hack
	if (os.name=='nt'):
		driver = webdriver.Chrome(chrome_options=chrome_options,executable_path='./chromedriver_win32/chromedriver.exe')#windows
	else: #(os.name=='posix'):
		driver = webdriver.Chrome(chrome_options=chrome_options,executable_path=executable_path) # for mac 

	return driver


def compile_logs(log_folder,interval_update=False):
	if not os.path.isdir(log_folder):
		return [0]

	logs = [ (os.path.join(log_folder, logname)) for logname in os.listdir(log_folder) if logname.endswith('.log')]

	rows = []
	for log in logs:
		with open(log) as f:
			rows.extend(f.read().strip().split(' '))

	if not interval_update: # dont write each interval update
		with open((os.path.join(log_folder, "aggregate log")),'w+') as f:
			f.write(" ".join(rows))

	rows = [int(row) for row in rows if row.isdigit()]

	return rows


def update_database(log_folder,database_path):
	if not (os.path.isdir(log_folder) and os.path.exists(database_path)):

		if os.path.exists(database_path):
			df = pd.read_csv(database_path,chunksize = 100000)
			total = sum([len(chunk) for chunk in df])
			return 0, total
		else:
			return 0,0

	rows = compile_logs(log_folder)

	try:
		df = pd.read_csv(database_path)
		df.iloc[rows] = 1
		total = len(df)
		completed = df['download'].sum()
		updated_database = database_path[:-4]+"-copy.csv"
		df.to_csv(updated_database)
		os.remove(database_path)
		os.rename(updated_database,database_path)
		print("{}/{} filings have been downloaded: {:.2%} complete. Contiuing from last download. \n".format(str(completed), str(total), (completed/total) ))
	except:
		print("An error occured at the update, please redo this step.")
		return

	[os.remove((os.path.join(log_folder, logname))) for logname in os.listdir(log_folder) if logname.endswith('.log')] # remove all the redundant logs
	return completed, total



def create_folder(folder_name):
	try:
		os.makedirs(folder_name)
	except OSError as e:
		if e.errno != errno.EEXIST:
			raise
	return


def download_data_chunk(chunk):

	driver = configure_web_driver()

	log_folder = "Download Logs"
	create_folder(log_folder)
	log_name = "{}-{}-download.log".format(str(chunk.index[0]),str(chunk.index[-1]))
	with open(os.path.join(log_folder,log_name),"a") as log:
		for row_index, row in chunk[chunk['download']==0].iterrows():

			conm = row['conm']
			htm = row['path']
			filing = row['type']
			cik = row['cik']
			date = row['date']
			yr_qtr = "{}-QTR{}".format(date[:4],ceil(int(date[5:7])/3))

			if ('/' in filing):
				filing = quote(filing, safe='') # use percent encoding to escape the slash # use urllib.parse.unquote(encoded_str,'utf8') to decode
			filing_folder_name = '-'.join([str(row_index),str(filing),str(cik)])
			filing_folder_path = '/'.join([datafolder, yr_qtr , filing_folder_name])

			# print('Start fetching URL to', conm, filing, 'filed on', date, '...')
			# start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
			try:
				driver.get(htm)
				create_folder(filing_folder_path)

				for a in driver.find_elements_by_xpath('.//a'):
					url = a.get_attribute('href')    # print(a.get_attribute('href'))
					if(url.startswith(PREFIX)):
						filename = url.split('/')[-1]
						wget.download(url , filing_folder_path + '/'+ filename)
				
				# end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
				# print('Success!', start_time, ' --> ', end_time,'\n')

				log.write(str(row_index)+" ")
				log.flush()
			except:
				print("Error in downloading this file.",htm)
				# end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
				# print('Error!', start_time, ' --> ', end_time, '\n')
	return


# using threadPool, inherently multithreaded
def start_download(database,n_threads=9):

	log_folder = "Download logs"

	pool = ThreadPool(n_threads) # instantiate multiple threads

	df = pd.read_csv(database,chunksize=10000)
	pool.map(download_data_chunk, df) # run the threads	
	pool.close() 
	pool.join() # wait for all to finish
	
	update_database(log_folder ,database)

	print("all done.")
	return

def update(start,interval,log_folder,count,total):

	log_folder = "Download logs"
	no_intervals = 0

	while(True):
		end = time.time()
		seconds_elapsed = end - start
		if seconds_elapsed > (no_intervals+1) * interval:

			rows = compile_logs(log_folder,interval_update=True)
			completed = len(rows)
			eta = int(seconds_elapsed / (completed/total))
			eta_str = datetime.timedelta(seconds=eta)
			total_completed = completed + count


			print("This program has run for {:.2f} hours, and downloaded {} filings, at a rate of {:.2f} filings per second.".format((seconds_elapsed/3600),
			str(completed), (completed/seconds_elapsed)))
			print("{}/{} filings have been downloaded: {:.2%} complete. Estimated time for completion: {}.\n".format(str(total_completed), str(total), (total_completed/total), eta_str))
			no_intervals+=1


if __name__ == '__main__':

	print("Preparing database...")
	database = IndexDownloader.download_and_convert(year=2016)
	print("Database preparation successful.")

	PREFIX = "https://www.sec.gov/Archives/edgar/data/" # common prefix for data files

	datafolder = "Downloaded data files"
	create_folder(datafolder)

	log_folder = "Download logs"

	print("\nStart downloading filings. This will take a while...\n")
	count, total = update_database(log_folder ,database)

	start_time = time.time()
	n_threads = 8
	update_p1 = Process(target=update,args=(start_time,60,log_folder,count,total))
	download_p2 = Process(target=start_download,args=(database,n_threads,))
	download_p2.start()
	update_p1.start()
	download_p2.join()
	print("\nDownloading complete.")
	exit()

