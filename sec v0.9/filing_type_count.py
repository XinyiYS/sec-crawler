# import sklearn
import pandas as pd
import numpy as np
csvs = [ "Database files/2017-QTR1.csv", "Database files/2017-QTR4.csv", "Database files/2018-QTR1.csv"]

# filing_dict = {}
# for csv in csvs:
# 	df = pd.read_csv(csv,usecols  = ['filing'])
# 	for i,count in df['filing'].value_counts().iteritems():
# 		if i in filing_dict:
# 			filing_dict[i] += count
# 		else:
# 			filing_dict[i] = count


import json
import pickle

# with open('filing dict ', 'wb') as file:
     # file.write(pickle.dumps(filing_dict)) # use `pickle.loads` to do the reverse

with open('filing dict','rb') as r:
	di = pickle.loads(r.read())

print(di)
# print(pd.DataFrame.from_dict(filing_dict))

# df = pd.read_csv("Database files/2017-QTR3.csv",usecols  = ['filing'])
#
# print(df['filing'].value_counts())


# for i,item in (df['filing'].value_counts().iteritems()):
	# print(i,item)
	# exit()

# print(df[df['filing']=='3']['filing'].value_counts())
# print(df[df['filing'].str.contains('10-Q')]['filing'].value_counts())
# subdf = df[ df['filing'].str.contains("8") ]
# subdf = subdf[subdf['filing'].str.contains('K')]
# subdf = subdf[subdf['filing']!='10-Q']
# subdf = subdf[subdf['filing']!='NT 10-']
# subdf = subdf[subdf['filing']!='10-Q/A']
# subdf = subdf[subdf['filing']!='10-Q/A']



# csv = "Database files/2017-QTR1.csv"
# csv = "Database files/2017-QTR4.csv"
# csv = "Database files/2018-QTR1.csv"

# print(os.listdir("Database files"))
# for path in os.listdir("Database files"):
# 	df =  pd.read_csv(os.path.join("Database files",path))
# 	subdf = df[ ( df['filing'].str.contains("Q") & df['filing'].str.contains("10") )]
# 	subdf.to_csv('10Q.csv')
# 	size = os.path.getsize("10Q.csv")
# 	print("size of {} is {}".format(str(path),str(size)))
import re


# print(os.listdir("Downloaded data files"))

a = 123
regex = re.compile(str(a)+ " "+"123")
regexp = re.compile("Item 8\\.")
print(regexp.search("Item 8.asdasd").group())



# a = ("a","a")
# b = ("b","a")
# print(set(a).issubset(b))

