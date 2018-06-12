import random,time,itertools,threading,re,datetime
import urllib,csv,os, errno, wget
from re import search
from urllib.parse import quote,unquote
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool 
from multiprocessing import Process
import shutil
import IndexDownloader
import numpy as np
from math import ceil
import pandas as pd 
from bs4 import BeautifulSoup
import requests


def compile_logs(log_folder,interval_update=False):
	if not os.path.isdir(log_folder):
		return [0]

	logs = [ (os.path.join(log_folder, logname)) for logname in os.listdir(log_folder) if logname.endswith('.log')]

	filing_indices = []
	for log in logs:
		with open(log) as f:
			filing_indices.extend(f.read().strip().split(' '))

	with open((os.path.join(log_folder, "aggregate log")),'a') as f:
			f.write(" "+" ".join(filing_indices)+" ")

	with open((os.path.join(log_folder, "aggregate log")),'r') as agg_log:
		filing_indices = agg_log.read().strip().split(' ')

	filing_indices = np.array(np.unique([int(filing_index) for filing_index in filing_indices if filing_index.isdigit()]))
	return filing_indices

def clear_logs(log_folder):
	if not os.path.isdir(log_folder):
		return 
	try:
		os.remove(log_folder+"/aggregate log")
		[os.remove((os.path.join(log_folder, logname))) for logname in os.listdir(log_folder) if logname.endswith('.log')] # remove all the redundant logs
		return
	except:
		return

def update_database(log_folder,database_path):
	if not (os.path.isdir(log_folder) and os.path.exists(database_path)):

		if os.path.exists(database_path):
			df = pd.read_csv(database_path,chunksize = 100000)
			total = sum([len(chunk) for chunk in df])
			return 0, total
		else:
			return 0,0

	filing_indices = compile_logs(log_folder)
	try:
		df = pd.read_csv(database_path)
		total = len(df)
		completed = 0

		if len(df.loc[df['index'].isin(filing_indices)]) !=  0:

			df.loc[df['index'].isin(filing_indices), 'download'] = int(1)
			completed = df['download'].sum()
			updated_database = database_path[:-4]+"-copy.csv"
			df.to_csv(updated_database,index=False)
			os.remove(database_path)
			os.rename(updated_database,database_path)
	except:
		print("An error occured at the update, please redo this step.")
		return

	return completed, total


def update_all_csvs(database_folder):
	database_folder = "Database files" # or use crawlerfolder
	paths = ([ (os.path.join(database_folder, csv)) for csv in os.listdir(database_folder) if csv.endswith('.csv')])

	count,total = 0 , 0
	for path in paths:
		c , t = update_database(log_folder,path)
		count += c
		total += t

	clear_logs(log_folder)
	print("{}/{} filings have been downloaded: {:.2%} complete. Continuing from last download. \n".format(str(count), str(total), (count/total) ))
	
	return count,total


def create_folder(folder_name):
	try:
		os.makedirs(folder_name)
	except OSError as e:
		if e.errno != errno.EEXIST:
			raise
	return

def get_urls(url):
	soup = BeautifulSoup(requests.get(url).text,'lxml')
	return [link.get('href') for  link in soup.find_all('a') if link.get('href').startswith('/Archives/edgar/data/')] # COMMON_PREFIX = '/Archives/edgar/data/'

# single download
def get_file(filing_folder_path,url):
	url= "".join(["https://www.sec.gov",url])
	filename = url.split('/')[-1]
	wget.download(url , filing_folder_path + '/'+ filename, bar=None)
	return (url+"\n")


def download_data_chunk(chunk, filing ):

	log_folder = "Download Logs"
	create_folder(log_folder)
	datafolder = "Downloaded data files"

	log_name = "{}-{}-download.log".format(str(chunk.index[0]),str(chunk.index[-1]))

	process,download_entire,iotime = [],[],[]
	counter = 0
	start_time = time.time()
	update_count = 0

	with open(os.path.join(log_folder,log_name),"a") as log:

		sub_chunk = chunk[chunk['filing'] == filing]
		for i_, row in sub_chunk[sub_chunk['download']==0].iterrows():
		# for row_index, row in chunk[chunk['download']==0].iterrows(): # changed for good
			stamps = []
			
			# stamps[0]
			stamps.append(time.time())
			filing_index = row['index']
			comn = row['comn']
			htm = row['htm']
			filing = row['filing']
			cik = row['cik']
			date = row['date']
			date_str = "".join(str(date).split("-"))
			yr_qtr = "{}-QTR{}".format(date[:4],ceil(int(date[5:7])/3))

			if ('/' in filing):
				filing = quote(filing, safe='') # use percent encoding to escape the slash # use urllib.parse.unquote(encoded_str,'utf8') to decode
			filing_folder_name = ' '.join([str(filing_index),str(cik),str(date_str),str(filing)])
			filing_folder_path = '/'.join([datafolder, yr_qtr , filing ,  filing_folder_name])

			# print('Start fetching URL to', comn, filing, 'filed on', date, '...')
			# start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
			
			create_folder(filing_folder_path)

			urls = get_urls(htm)

			# stamps[1]
			stamps.append(time.time())

			try:

				pool = ThreadPool(len(urls)) # instantiate multiple threads
				all_urls = (htm+"\n") + "".join(pool.starmap(get_file, zip(itertools.repeat(filing_folder_path), urls)))
				pool.close() 
				pool.join() # wait for all to finish
				# stamps[2]
				stamps.append(time.time())

				with open(filing_folder_path+'/'+'download.log', 'w', newline='') as download_log:
					download_log.write(all_urls)

				log.write(str(filing_index)+" ")
				if (time.time()- start_time) > update_count * 60:
					log.flush()
					update_count += 1

				# stamps[3]
				stamps.append(time.time())
				
				process.append(stamps[1]-stamps[0])
				download_entire.append(stamps[2]-stamps[1])
				iotime.append(stamps[3]-stamps[2])
				
			except:
				with open(os.path.join(log_folder,'error log'),"a") as error_log:
					error_log.write(htm+"\n")

			counter+=1
			if( counter % 100==0):
				# timelog.write("For {} filings. Process avg: {:.3f} seconds. Latency avg: {:.3f} seconds. Iotime avg: {:.3f}".format(str(counter),np.mean(process),np.mean(latency),np.mean(iotime)))
				print("For {} filings. Process avg: {:.3f} seconds. Documents downloading avg: {:.3f}. \
					Iotime avg: {:.3f}".format(str(counter),np.mean(process), np.mean(download_entire),np.mean(iotime)))

	return


# using threadPool, inherently multithreaded
def start_download(database_folder,filing,n_threads=9 ):

	log_folder = "Download logs"

	database_folder = "Database files"
	csvs = sorted([ (os.path.join(database_folder, csv)) for csv in os.listdir(database_folder) if csv.endswith('.csv')])[::-1]
	for csv in csvs:

		pool = ThreadPool(n_threads) # instantiate multiple threads
		df = pd.read_csv(csv,chunksize=10000) # df is just an io iterator
		pool.starmap(download_data_chunk, zip(df, itertools.repeat(filing))) # run the threads	
		pool.close() 
		pool.join() # wait for all to finish
		
		update_database(log_folder ,csv)

	print("all done.")
	return

def update(start,interval,log_folder,count,total):

	log_folder = "Download logs"
	no_intervals = 0

	while(True):
		end = time.time()
		seconds_elapsed = end - start
		if seconds_elapsed > (no_intervals+1) * interval:

			filing_indices = compile_logs(log_folder,interval_update=True)
			completed = len(filing_indices)
			if completed != 0:
				eta = int(seconds_elapsed / (completed/total))
				eta_str = datetime.timedelta(seconds=eta)
			else:
				eta_str = "no estimation available yet"
			total_completed = completed + count

			print("This program has run for {:.2f} hours, and downloaded {} filings, at a rate of {:.2f} filings per second.".format((seconds_elapsed/3600),
			str(completed), (completed/seconds_elapsed)))
			print("{}/{} filings have been downloaded: {:.2%} complete. Estimated time for completion: {}.\n".format(str(total_completed), str(total), (total_completed/total), eta_str))
			no_intervals+=1
	return


if __name__ == '__main__':

	try:
		from_year = 2017
		to_year = 2018
		print("Preparing database...Please do not interrupt the program.")
		database_folder = IndexDownloader.prepare_database(begin=from_year, end=to_year)
		print("Database preparation successful.")

		datafolder = "Downloaded data files"
		create_folder(datafolder)

		log_folder = "Download logs"

		print("\nStart downloading filings. This will take a while...\n")
		count,total = update_all_csvs(database_folder) # 	count, total = update_database(log_folder ,database)

		start_time = time.time()
		n_threads = 3
		filing = '10-K'
		update_p1 = Process(target=update,args=(start_time,60,log_folder,count,total))
		download_p2 = Process(target=start_download,args=(database_folder,filing,n_threads,))
		download_p2.start()
		# update_p1.start()

		update(start_time ,60,log_folder,count,total)
		download_p2.join()
		update_p1.terminate()
		print("\n all processed terminated")
		print("\nDownloading complete.")
		exit()

	except KeyboardInterrupt:
	    print ('Interrupted')
	    try:
	        sys.exit(0)
	    except SystemExit:
	        os._exit(0)
