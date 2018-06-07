# Generate the list of index files archived in EDGAR since start_year (earliest: 1993) until the most recent quarter

# (download crawler urls into a stata database)
print("PART 1: This part downloads crawler urls into a folder named Downloaded index files")
print()

import os
from selenium import webdriver
import time,requests,errno


# Generate the list of index files archived in EDGAR since start_year (earliest: 1993) until the most recent quarter

import datetime

current_year = datetime.date.today().year
current_quarter = (datetime.date.today().month - 1) // 3 + 1


start_year = 2017 # choose the year to start

years = list(range(start_year, current_year))
quarters = ['QTR1', 'QTR2', 'QTR3', 'QTR4']
history = [(y, q) for y in years for q in quarters]
for i in range(1, current_quarter + 1):
    history.append((current_year, 'QTR%d' % i))
urls = ['https://www.sec.gov/Archives/edgar/full-index/%d/%s/crawler.idx' % (x[0], x[1]) for x in history]
urls.sort()

print("Year {} to current date is seleted. All {} quarters are used".format(str(start_year),len(quarters)))
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


# uncomment this line below to create a csv that queries the entire database downloaded
# database.to_csv("query.csv") 


# download all the files for each filing in the query.csv
print("*************************************************************************")
print("PART 2: This part downloads all the files for each filing into a folder named: 'Downloaded data files' ,")
print("PART 2: Docments for each filing is downloaded to its respectively created subfolder.")
print()
print()


import urllib,csv,random
import os, errno,  wget
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


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


                print('Start fetching URL to', comn, filing, 'filed on', date, '...')
                start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())


                path = os.path.join(os.getcwd(), 'chromedriver')  # this is for mac users
                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--disable-gpu')
                # driver = webdriver.Chrome(chrome_options=chrome_options,executable_path=path) # for mac 
                driver = webdriver.Chrome(chrome_options=chrome_options,executable_path='./chromedriver_win32/chromedriver.exe')#windows


                try:
                    driver.get(htm)
                    foldername = comn+"-"+filing+"-"+cik # use * for convenient coding separation
                    path = datafolder+ '/' + foldername
                    try:
                        os.makedirs(path)
                    except OSError as e:
                        if e.errno != errno.EEXIST:
                            raise
                    
                    with open(path+'/'+'download.log', 'w', newline='') as download_log:
                        download_log.write("Filing url is: " +" "+htm+"\n")
                        download_log.write("\n")

                        # print(len(driver.find_elements_by_xpath('.//a')))
                        for a in driver.find_elements_by_xpath('.//a'):
                            url = a.get_attribute('href')    # print(a.get_attribute('href'))
                            PREFIX = "https://www.sec.gov/Archives/edgar/data/" # common prefix for data files

                            if(url.startswith(PREFIX)):
                                filename = url.split('/')[-1]
                                wget.download(url , path + '/'+ filename)
                                download_log.write("filename is : " +filename +"\n")
                                download_log.write("link is : "+ url + "\n")
                    
                    time.sleep(3 + random.random() * 3)
                    filing_date = driver.find_element_by_xpath('//*[@id="formDiv"]/div[2]/div[1]/div[2]').text
                    period_of_report = driver.find_element_by_xpath('//*[@id="formDiv"]/div[2]/div[2]/div[2]').text
                    form_text = driver.find_element_by_xpath('//*[@id="formDiv"]/div/table/tbody/tr[2]/td[3]/a').text
                    form_link = driver.find_element_by_link_text(form_text).get_attribute('href')
                    end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    print('Success!', start_time, ' --> ', end_time, '\n')
                    log_row = log_row + str(start_time)+str( end_time)+ str( filing_date)+str( period_of_report) +str( form_link)

                except:
                    end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    print('Error!', start_time, ' --> ', end_time, '\n')
                    log_row = log_row + str(start_time)+str( end_time)+ 'ERROR!'
                driver.quit()

                logwriter.writerow(log_row)


print("All downloading complete.\n")

