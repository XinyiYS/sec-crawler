from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool 
from multiprocessing import Process
from bs4 import BeautifulSoup
import requests
from os import walk
import os,re
import sys

import Finder_10K, Parser_10K


def check_input(cik,year,qt,filing,item):
	if not isinstance(cik, int) and isinstance(year, int) and isinstance(qt, int):
		print("Wrong year or quarter or cik format")
		return

def get_filing_folder_path(cik,yr_qtr,filing,item):
	datafolder = "Downloaded data files"
	path = os.path.join(yr_qtr,filing)
	def match(filing_folder,cik,yr_qtr,filing):
		regex = re.compile(str(cik)+" "+ str(yr_qtr[:4])+ "\d{4}" + " "+ str(filing) )
		return True if regex.search(filing_folder) is not None else False

	filing_folders = [os.path.abspath(os.path.join(datafolder,path,filing_folder)) for filing_folder in  os.listdir(os.path.join(datafolder,path))  if match(filing_folder,cik,yr_qtr,filing) ] 
	return filing_folders


def get_10k_htm(inputs):

	cik = inputs[0]
	yr_qtr = inputs[1]
	filing = inputs[2]
	item = inputs[3]

	filing_folder_paths = get_filing_folder_path(cik, yr_qtr, filing,item)

	for filing_folder_path in filing_folder_paths:
		htm = Finder_10K.get_10k_htm(filing_folder_paths[0])
		save_to_file = "{}-{}-{}-{}".format(cik,yr_qtr,filing,item)
		Parser_10K.get(htm, item ,save_to_file = save_to_file, render=True)
	return 


def check_if_continue():
	ans = input("Do you wish to continue:? (Y/N)")
	return str(ans).lower()=='y'

def get_user_input():

	satisfied = False
	while not satisfied:
		cik  = int(input("Enter the cik number: "))
		year = int(input("Enter the year (e.g. 2012): "))
		qt = int(input("Enter the quarter (e.g. 3): "))
		filing = (input("Enter the form type (e.g. 10-K): "))
		item= (input("Enter the section (e.g. 1A): "))
		satisfied = input("for CIK :{}, in {}-QTR{}. Form is {} . Item is {}.  Correct? (Y/N)".format(cik, str(year) ,str(qt),str(filing),str(item))).lower()=="y"
	yr_qtr = "{}-QTR{}".format(year,qt)

	return [ str(cik),yr_qtr,filing,item]

def main():
	if_continue = True
	while True and if_continue:

		inputs = get_user_input()
		# try:
		get_10k_htm(inputs)
		# except:
			# print("There seems to be some error with getting the htm. Try something else.")
		if_continue = check_if_continue()	

	print('Bye')
	sys.exit(0)



if __name__ == '__main__':
	    try:
	        main()
	    except KeyboardInterrupt:
	        print ('Bye')
	        sys.exit(0)
	    except ValueError:
	    	sys.exit(0)





