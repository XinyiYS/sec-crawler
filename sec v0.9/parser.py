from bs4 import BeautifulSoup
import requests
import urllib
import re

soup = BeautifulSoup (open("0000320193-17-000070.txt"),'lxml')


def get_delim_text(soup):
	text = soup.get_text()
	# break into lines and remove leading and trailing space on each
	lines = (line.strip() for line in text.splitlines())
	# break multi-headlines into a line each
	chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
	# drop blank lines
	text = '\n'.join(chunk for chunk in chunks if chunk)
	return text
print(get_delim_text(soup))
