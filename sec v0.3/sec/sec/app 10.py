import random,time,itertools,threading,re
from re import search
import urllib,csv,os, errno, wget
from urllib.parse import quote,unquote
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool 
import IndexDownloader

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

def read_log(log_path):

	if not(os.path.isfile(log_path) and os.path.getsize(log_path) > 0):
		return (-1,[])
	else:
		with open(log_path,'r') as log:
			content = log.readlines()
			counter = int(content[2])
			indices = sorted([int(s) for s in re.findall(r'\b\d+\b', content[3])])
	return (counter,indices)


def download_data(path):

	driver = configure_web_driver()

	crawlerfolder = "Downloaded index files" # for path reference

	# for logging
	log_header = search('\d{4}-QTR\d{1}', path).group(0)+'-log'
	log_path = os.path.join(crawlerfolder, log_header)
	error_indices = []
	
	# check if log_header file exists, if True, continue from last download   
	counter,missed_indices = read_log(log_path)
	
	with open(path,'r') as file, open(log_path,'a') as log: 
		for index,line in enumerate(file):  # index is 0-based and content starts from index == 9, row number 10 in the file
			row_index = index + 1
			if( row_index < 10  or (row_index <= counter and row_index not in missed_indices)):
				continue # skip downloading
			comn = line[:62].strip()
			filing = line[62:72].strip()
			cik = line[72:83].strip()
			date = line[83:96].strip()
			htm = line[96:].strip()
			if(row_index==21):
				print("downloaded a section,let's compare time")
				driver.quit()	
				return
			print('Start fetching URL to', comn, filing, 'filed on', date, '...')
			start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
			try:
				driver.get(htm)
				if ('/' in filing):
					filing = quote(filing,safe='') # use percent encoding to escape the slash # use urllib.parse.unquote(encoded_str,'utf8') to decode
				filing_folder_name = '-'.join([str(row_index),filing,cik])
				filing_folder_path = '/'.join([datafolder, log_header[:-4] , filing_folder_name])
				try:
					os.makedirs(filing_folder_path)
				except OSError as e:
					if e.errno != errno.EEXIST:
						raise
				# # the download log is disabled for more efficiency
	    		# thread_id = threading.get_ident()
	    		# with open("-".join([str(thread_id), 'test.log']), 'a', newline='') as download_log:
	    			# download_log.write('****************************************************************\n')
	    			# download_log.write("Filing url is: " +" "+htm+"\n\n")
				for a in driver.find_elements_by_xpath('.//a'):
					url = a.get_attribute('href')    # print(a.get_attribute('href'))
					if(url.startswith(PREFIX)):
						filename = url.split('/')[-1]
						wget.download(url , filing_folder_path + '/'+ filename)
						# download_log.write("filename is : " +filename +"\n")
						# download_log.write("link is : "+ url + "\n\n")
				end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
				print('Success!', start_time, ' --> ', end_time, '\n')
			except:
				end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
				print('Error!', start_time, ' --> ', end_time, '\n')
				error_indices.append(row_index)

	    	# update the log every 10 filings, each uses only 0.02 seconds
			# if( ( (row_index) % 10 == 0) and (row_index > counter)):  	       
	        	# s = time.time() 	        	
			log.truncate(0) # clear
			log.write( log_header[:-4]+'\n')
			log.write("1st row: counter. 2nd row: missed row indices.\n")
			log.write("{}\n{}\n".format(str(row_index),error_indices))
	       		# print('logging used: {}'.format((time.time()-s)))
	return 

# using threadPool, inherently multithreaded
def start(n_threads=10):
	IndexDownloader.download_index_files(2000)

	start = time.time()
	pool = ThreadPool(n_threads) # instantiate multiple threads
	pool.map(download_data, paths) # run the threads
	pool.close() 
	pool.join() # wait for all to finish
	end = time.time()
	print(end-start)
	print("all done")

	return

def checkStatus(clear=False):
	crawlerfolder = "Downloaded index files"
	paths = [ (os.path.join(crawlerfolder, filename)) for filename in os.listdir(crawlerfolder) if filename.endswith('-log')]

	def get_missed_count(logname):
		if not(os.path.isfile(logname) and os.path.getsize(logname) > 0):
			return 0
		else:
			with open(logname,'r') as log:
				return len([int(s) for s in re.findall(r'\b\d+\b', log.readlines()[3])])  # return the number of missed filings
			
	sum = sum([get_missed_count(path) for path in paths])
	print("A total of {} files are missed".format(str(sum)))
	# print([get_missed_count(path) for path in paths].index(1))

	def clear_log(logname):
		with open(logname,'w+') as log: pass
		return
	if clear:
		print("Clearing all the logs, so when re-run, everything will be downloaded again.\n")
		[clear_log(logname) for logname in paths]	
	return

PREFIX = "https://www.sec.gov/Archives/edgar/data/" # common prefix for data files

crawlerfolder = "Downloaded index files"
paths = [ (os.path.join(crawlerfolder, filename)) for filename in os.listdir(crawlerfolder) if filename.endswith('.txt')]

datafolder = "Downloaded data files"
try:
    os.makedirs(datafolder)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

start(n_threads=len(paths))
