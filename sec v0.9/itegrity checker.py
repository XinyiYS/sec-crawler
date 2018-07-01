from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool 
from multiprocessing import Process
import requests
from os import walk
import os,re
import pandas as pd

def check_total_count(database_folder, datafolder, filing):

	csvs = [ os.path.join(database_folder,csv) for csv in os.listdir(database_folder)]
	regex= re.compile("\d{4}-QTR\d")
	yr_qtrs = [regex.search(csv).group() for csv in csvs]

	total_in_csvs, total_1_in_csvs, total_filing_counts_all = 0,0,0
	for csv,yr_qtr in zip(csvs, yr_qtrs):
		df = pd.read_csv(csv,chunksize=100000,usecols = ['filing','download'])
		
		total_in_csv,total_1_in_csv = 0,0 
		for chunk in df:
			subchunk = chunk[chunk['filing'].str.contains("K") ]
			subchunk =  subchunk[subchunk['filing'].str.contains("10")]

			total_in_csv += len( subchunk )
			total_1_in_csv += sum(subchunk['download'] )  

		# total_in_csv = sum  (   len( chunk [ chunk['filing'].str.contains("10") & (chunk['filing'].str.contains("K")) ]  )  )
		# total_1_in_csv = sum  (   sum( chunk [ chunk['filing'].str.contains("10") & (chunk['filing'].str.contains("K")) ] ['download'] )  )
		try:
			def check_if_complete(filing_folder):

				docs = os.listdir(filing_folder)

				[os.remove(os.path.join(filing_folder,doc)) for doc in docs if doc.endswith(".tmp")] 

				supposed_docs = 0  
				with open(os.path.join(filing_folder,"download.log"), "r" )as r:
					supposed_docs = [ line.strip().split("/")[-1] for line in r.readlines()[1:]  ]
				supposed_docs.append("download.log")

				issubset = set(supposed_docs).issubset((docs))
				if not issubset:
					# WRITE THE ERROR
					with open("errors","a") as a:
						a.write(filing_folder+"\n")
					
				return issubset

			total_filing_counts_single = len([dirpath for (dirpath, dirnames, filenames) in os.walk(os.path.join(datafolder, yr_qtr,"10-K")) 
					if "download.log" in os.listdir(dirpath) and check_if_complete(dirpath)  ])

		except Exception as e:
			print(e)
			total_filing_counts_single = 0

		print("For filing: {}, and period : {} the supposed total is : {} , marked downloaded in csv is : {}\
 the actual downloaded is : {} .".format(filing ,yr_qtr,str(total_in_csv),str(total_1_in_csv),str(total_filing_counts_single)))
		total_in_csvs += total_in_csv
		total_1_in_csvs += total_1_in_csv
		total_filing_counts_all += total_filing_counts_single
	return	total_in_csvs, total_1_in_csvs, total_filing_counts_all

database_files_folder = "Database files"
datafolder = "Downloaded data files"
filing = "10-K"

a,b,c =check_total_count(database_files_folder,datafolder,filing_folder)
print(a,b,c)


def check_1_in_csvs():
	return

def check_0_in_csvs():
	return