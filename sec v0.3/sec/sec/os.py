
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os,wget
import re

import urllib,time,errno
from urllib.parse import quote,unquote
import multiprocessing as mp
import IndexDownloader 

print(help(IndexDownloader.download_index_files))

crawlerfolder = "Downloaded index files"
paths = [ (os.path.join(crawlerfolder, filename)) for filename in os.listdir(crawlerfolder) if filename.endswith('-log')]

def get_missed_count(logname):
	if not(os.path.isfile(logname) and os.path.getsize(logname) > 0):
		return 0
	with open(logname,'r') as log:
		content = log.readlines()
		count = len([int(s) for s in re.findall(r'\b\d+\b', content[3])])
		return count
sum = sum([get_missed_count(path) for path in paths])
print(sum)
# print([get_missed_count(path) for path in paths].index(1))

def clear_log(logname):
	with open(logname,'w+') as log: pass
	return
[clear_log(logname) for logname in paths]	


