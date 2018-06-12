
import pandas as pd


import os
import numpy as np

crawlerfolder = "Downloaded index files"

paths = []
for filename in os.listdir(crawlerfolder):
    if filename.endswith(".txt"): 
    	path = (os.path.join(crawlerfolder, filename))
    	paths.append(path)


def create_query_csv(paths):

	columns = ['index','comn','filing','cik','date','htm']
	data = []
	for path in paths:
		with open(path,'r') as file:
			for index,line in enumerate(file):  # index is 0-based and content starts from index == 9
				if( index < 9 ):
					continue
				comn = line[:62].strip()
				filing = line[62:72].strip()
				cik = line[72:83].strip()
				date = line[83:96].strip()
				htm = line[96:].strip()
				row = (index,comn,filing,cik,date,htm)
				data.append(row)

	return pd.DataFrame(data=data,columns=columns)
	
create_query_csv(paths).to_csv('query.csv')

