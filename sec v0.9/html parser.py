from bs4 import BeautifulSoup
import requests
import urllib

url = "https://www.sec.gov/Archives/edgar/data/1652044/000165204418000007/goog10-kq42017.htm"
def get_urls(url):
	soup = BeautifulSoup(requests.get(url).text,'lxml')
	return [link.get('href') for  link in soup.find_all('a') if link.get('href').startswith('/Archives/edgar/data/')] # COMMON_PREFIX = '/Archives/edgar/data/'


soup = BeautifulSoup (open("pharma024-20161231.htm"),'lxml')


# soup = BeautifulSoup(page, 'html.parser')

content = soup.prettify()
content  = soup.get_text()


import re

result = re.findall("PART I.*?PART II", content, flags=re.S)
print(result)

exit()
# print(result.group(0))