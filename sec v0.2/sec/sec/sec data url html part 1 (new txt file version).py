import os
from selenium import webdriver
import time,requests,errno


# Generate the list of index files archived in EDGAR since start_year (earliest: 1993) until the most recent quarter

# (download crawler urls into a stata database)
print("This part downloads crawler urls into a stata database named: 'edgar_htm_idx.db' ")
import datetime

current_year = datetime.date.today().year
current_quarter = (datetime.date.today().month - 1) // 3 + 1

start_year = 2016 # choose the year to start

years = list(range(start_year, current_year))
quarters = ['QTR1', 'QTR2', 'QTR3', 'QTR4']
history = [(y, q) for y in years for q in quarters]
for i in range(1, current_quarter + 1):
    history.append((current_year, 'QTR%d' % i))
urls = ['https://www.sec.gov/Archives/edgar/full-index/%d/%s/crawler.idx' % (x[0], x[1]) for x in history]
urls.sort()

print("Year {} to current date is seleted. All the quarters are used".format(str(start_year)))
print("You have a total of {} quarters of filing links indices to download".format(len(urls)))


crawlerfolder = "Downloaded index files"
try:
    os.makedirs(crawlerfolder)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

for url,hist in zip(urls,history):
	year = hist[0]
	quarter = hist[1]
	print("Downloading from : =>      "+ url)
	request = requests.get(url,timeout = 10)
	filename = str(year)+'-'+str(quarter)
	path = crawlerfolder + '/' + filename+ '.txt'
	with open(path, 'wb') as fd:
		    [fd.write(chunk) for chunk in request.iter_content(chunk_size=20480)]
	print(url, 'downloaded and wrote to txt')
