from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool 
import urllib,csv,random
import os, errno,  wget
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def download_data():

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

	    crawlerfolder = "Downloaded index files"
	    paths = [ (os.path.join(crawlerfolder, filename)) for filename in os.listdir(crawlerfolder)]

	    for path in paths:
	    	print(path)
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

	                if(index==11):
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
	                    
	                    with open(path+'/'+'download.log', 'w', newline='') as download_log:
	                        download_log.write("Filing url is: " +" "+htm+"\n\n")

	                        # print(len(driver.find_elements_by_xpath('.//a')))
	                        for a in driver.find_elements_by_xpath('.//a'):
	                            url = a.get_attribute('href')    # print(a.get_attribute('href'))

	                            if(url.startswith(PREFIX)):
	                                filename = url.split('/')[-1]
	                                wget.download(url , path + '/'+ filename)
	                                download_log.write("filename is : " +filename +"\n")
	                                download_log.write("link is : "+ url + "\n")
	                    
	                    # time.sleep(random.uniform(0.02,0.05) )
	                    #filing_date = driver.find_element_by_xpath('//*[@id="formDiv"]/div[2]/div[1]/div[2]').text
	                    #period_of_report = driver.find_element_by_xpath('//*[@id="formDiv"]/div[2]/div[2]/div[2]').text
	                    #form_text = driver.find_element_by_xpath('//*[@id="formDiv"]/div/table/tbody/tr[2]/td[3]/a').text
	                    #form_link = driver.find_element_by_link_text(form_text).get_attribute('href')
	                    end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
	                    print('Success!', start_time, ' --> ', end_time, '\n')
	                    # log_row = log_row + str(start_time)+str( end_time)+ str( filing_date)+str( period_of_report) +str( form_link)
	                    # about 0.15 seconds for the above log lines


	                except:
	                    end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
	                    print('Error!', start_time, ' --> ', end_time, '\n')
	                    # log_row = log_row + str(start_time)+str( end_time)+ 'ERROR!'
	                
	                # logwriter.writerow(log_row)

	driver.quit()
	print("All downloading complete.\n")



start = time.time()
download_data()
end = time.time()
print(end-start)