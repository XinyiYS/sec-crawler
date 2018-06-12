import pandas as pd
import os
import numpy as np



def create_csv(path,startIndex):
	columns = ['index','comn','filing','cik','date','htm','download']
	data = []
	with open(path,'r') as file:
		for index,line in enumerate(file):  # index is 0-based and content starts from index == 9
			if( index < 9 ):
				continue
			comn = line[:62].strip()
			filing = line[62:72].strip()
			cik = line[72:83].strip()
			date = line[83:96].strip()
			htm = line[96:].strip()
			row = (index + startIndex - 8 ,comn,filing,cik,date,htm, 0 ) # 1-indexed counting for files.
																		# 0 is to indicate the download status : unfinished
			data.append(row)

	pd.DataFrame(data=data,columns=columns).to_csv(path[:-4]+".csv",index=False)
	return startIndex + len(data)


crawlerfolder = "Downloaded index files"
paths = sorted([ (os.path.join(crawlerfolder, filename)) for filename in os.listdir(crawlerfolder) if filename.endswith('.txt')])


