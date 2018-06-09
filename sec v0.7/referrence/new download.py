from bs4 import BeautifulSoup
import requests
import IndexDownloader
import wget
import itertools
import os,errno
from multiprocessing.dummy import Pool as ThreadPool 


def get_file(filing_folder_path,url):
	PREFIX_TO_ADD = "https://www.sec.gov"
	if url.startswith('/Archives/edgar/data/'):
		url = "".join([PREFIX_TO_ADD,url])
	filename = url.split('/')[-1]
	wget.download(url , filing_folder_path + '/'+ filename)
	return (url+"\n")

def create_folder(folder_name):
	try:
		os.makedirs(folder_name)
	except OSError as e:
		if e.errno != errno.EEXIST:
			raise
	return

create_folder('test')
filing_folder_path = 'test/'


COMMON_PREFIX  ='/Archives/edgar/data/'

import time

s = time.time()
url = "https://www.sec.gov/Archives/edgar/data/1084869/0001437749-18-009561-index.htm"
r  = requests.get(url)
data = r.text
soup = BeautifulSoup(data,'lxml')
# soup = BeautifulSoup(requests.get(url).text,'lxml')

print(time.time()-s)

urls = [link.get('href') for  link in soup.find_all('a') if link.get('href').startswith(COMMON_PREFIX)]
pool = ThreadPool(len(urls)) # instantiate multiple threads
results = (url+"\n") + "".join(pool.starmap(get_file, zip(itertools.repeat(filing_folder_path), urls)))

print(results)

pool.close() 
pool.join() # wait for all to finish
