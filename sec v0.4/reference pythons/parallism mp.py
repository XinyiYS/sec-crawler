from multiprocessing import Pool
from multiprocessing import Process
import multiprocessing as mp
import urllib,csv,random
import os, errno,  wget,time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def download_data(path):

	# to configure the webdriver 
	executable_path = os.path.join(os.getcwd(), 'chromedriver') 
	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_argument('--no-sandbox')
	chrome_options.add_argument('--headless')
	chrome_options.add_argument('--disable-gpu')
	# driver = webdriver.Chrome(chrome_options=chrome_options,executable_path=executable_path) # for mac 
	driver = webdriver.Chrome(chrome_options=chrome_options,executable_path='./chromedriver_win32/chromedriver.exe')#windows

	PREFIX = "https://www.sec.gov/Archives/edgar/data/" # common prefix for data files

	datafolder = "Downloaded data files"
	try:
	    os.makedirs(datafolder)
	except OSError as e:
	    if e.errno != errno.EEXIST:
	        raise

	with open('log.csv', 'w', newline='') as log:
	    logwriter = csv.writer(log)
	    with open(path,'r') as file:
	    	for index,line in enumerate(file):  # index is 0-based and content starts from index == 9		
	    		log_row = line
	    		if( index < 9 ):
	    			continue
	    		comn = line[:62].strip()
	    		filing = line[62:72].strip()
	    		cik = line[72:83].strip()
	    		date = line[83:96].strip()
	    		htm = line[96:].strip()
	    		if(index==10):
	    			print("downloaded a section,let's compare time")	
	    			break
	    		print('Start fetching URL to', comn, filing, 'filed on', date, '...')
	    		start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
	    		try:
	    			driver.get(htm)
	    			foldername = '-'.join([str(index),comn,filing,cik]) # index refers to the numeric index in the index text file
	    			path = '/'.join([datafolder, foldername])
	    			try:
	    				os.makedirs(path)
	    			except OSError as e:
	    				if e.errno != errno.EEXIST:
	    					raise
	    			pid = mp.current_process().pid
	    			with open("-".join([str(pid), 'test.log']), 'a', newline='') as download_log:
	    				download_log.write('****************************************************************\n')
	    				download_log.write("Filing url is: " +" "+htm+"\n\n")

	    				for a in driver.find_elements_by_xpath('.//a'):
	    					url = a.get_attribute('href')    # print(a.get_attribute('href'))

	    					if(url.startswith(PREFIX)):
	    						filename = url.split('/')[-1]
	    						wget.download(url , path + '/'+ filename)
	    						download_log.write("filename is : " +filename +"\n")
	    						download_log.write("link is : "+ url + "\n\n")
	    			end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
	    			print('Success!', start_time, ' --> ', end_time, '\n')
	    		except:
	    			end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
	    			print('Error!', start_time, ' --> ', end_time, '\n')
	                
	driver.quit()
	print("This filing's downloading complete.\n")
	return



if __name__ == '__main__':

	start = time.time()
	crawlerfolder = "Downloaded index files"
	paths = [ (os.path.join(crawlerfolder, filename)) for filename in os.listdir(crawlerfolder)]
	processes = [mp.Process(target=download_data, args=(path,)) for path in paths]

	# Run processes
	[p.start() for p in processes]
	   
	# Exit the completed processes
	[p.join() for p in processes]
	end = time.time()
	print(end-start)



