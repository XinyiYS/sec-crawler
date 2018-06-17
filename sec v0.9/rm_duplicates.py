from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool 
from multiprocessing import Process
from bs4 import BeautifulSoup
import requests
from os import walk
import os,re

def get_filing_folders(folder_to_clean,filing = '10-K'):
	return [dirpath for (dirpath, dirnames, filenames) in walk(folder_to_clean)]
					# if  len(dirpath.split("\\")) == 4 or len(dirpath.split("/")) == 4] # check if windows compatible

def get_urls(url):
	soup = BeautifulSoup(requests.get(url).text,'lxml')
	return [link.get('href') for  link in soup.find_all('a') if link.get('href').startswith('/Archives/edgar/data/')] 

def remove_duplicates(dirpath):
	download_log = "download.log"
	if(not os.path.exists(os.path.join(dirpath,download_log))): # checks if valid folder to clean
		return
	with open(os.path.join(dirpath,download_log),'r') as referrence:
		lines = referrence.readlines()
	files = os.listdir(dirpath)
	if(len(lines)-1 == len(files)-1):   # lines include all files and one master link, files include all files and one log
		# Nothing to remove
		return
	else:
		# htm = lines[0]
		# urls = get_urls(htm)
		# filenames = [url.split('/')[-1] for url in urls] # actual necessary files
		filenames = [url.split('/')[-1] for url in get_urls(lines[0])]
		filenames.append("download.log") # include download.log, NOT to be removed
		[os.remove(os.path.join(dirpath,file)) for file in files if file not in filenames]
	return

def clean_folder(folder_to_clean):
	dirpaths = get_filing_folders(folder_to_clean)
	[remove_duplicates(dirpath) for dirpath in dirpaths]
	# cleaners = 5
	# pool = ThreadPool(len(cleaners)) # instantiate multiple threads
	# pool.starmap(remove_duplicates, dirpaths)
	# pool.close() 
	# pool.join() # wait for all to finish
	return

folder_to_clean = "Downloaded data files"
print(folder_to_clean+ " starting removing dupliates")
clean_folder(folder_to_clean)
print(folder_to_clean + " finished removing duplicates")
