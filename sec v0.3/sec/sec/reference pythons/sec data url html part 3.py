# download all the files for each filing in the query.csv

import urllib,csv,random
import os, errno,  wget
import time
from selenium import webdriver

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

                driver = webdriver.Chrome(os.path.join(os.getcwd(), 'chromedriver'))  # this is for mac users
                

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


