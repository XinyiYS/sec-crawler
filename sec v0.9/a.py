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



from Exceptions import GetUrlException
from Exceptions import DownloadException
from Exceptions import LoggingException

try:
	# raise(GetUrlException("CANt fetch url",0))
	raise(Exception("htm link","disk locations"))
	# raise(LoggingException("logging path"))

except Exception as e:
	print((e.args[0]))



