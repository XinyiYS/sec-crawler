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

path  = "Database files/2017-QTR1.csv"
url = "https://www.sec.gov/Archives/edgar/data/1084869/0001437749-18-002143-index.htm"

def get_urls(url):
	soup = BeautifulSoup(requests.get(url).text,'lxml')
	return [link.get('href') for  link in soup.find_all('a') if link.get('href').startswith('/Archives/edgar/data/')] # COMMON_PREFIX = '/Archives/edgar/data/'

def get_file(filing_folder_path,url):
	url= "".join(["https://www.sec.gov",url])
	filename = url.split('/')[-1]
	wget.download(url , filing_folder_path + '/'+ filename, bar=None)
	return (url+"\n")




start = time.time()
# parallel 
for i in range(20):
	pool = ThreadPool(len(urls)) # instantiate multiple threads
	all_urls = (url+"\n") + "".join(pool.starmap(get_file, zip(itertools.repeat("parallel without reuse"), urls)))
	pool.close() 
	pool.join() # wait for all to finish


print(time.time()-start)

start = time.time()
for i in range(20):
# parrallel with connection open
	with requests.Session() as s:
		soup = BeautifulSoup(s.get(url).text,'lxml')
		urls = [link.get('href') for  link in soup.find_all('a') if link.get('href').startswith('/Archives/edgar/data/')] # COMMON_PREFIX = '/Archives/edgar/data/'
		pool = ThreadPool(len(urls)) # instantiate multiple threads
		all_urls = (url+"\n") + "".join(pool.starmap(get_file, zip(itertools.repeat("parallel with reuse"), urls)))
		pool.close() 
		pool.join() # wait for all to finish
print(time.time()-start)




