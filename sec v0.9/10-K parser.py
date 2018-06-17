from bs4 import BeautifulSoup
import requests
import urllib
import re

url = "https://www.sec.gov/Archives/edgar/data/1652044/000165204418000007/goog10-kq42017.htm"
def get_urls(url):
	soup = BeautifulSoup(requests.get(url).text,'lxml')
	return [link.get('href') for  link in soup.find_all('a') if link.get('href').startswith('/Archives/edgar/data/')] # COMMON_PREFIX = '/Archives/edgar/data/'


# soup = BeautifulSoup (open("pih-10k_123116.htm"),'lxml')
# content = soup.find_all("a",href=False)
# print(len(content))
# print(content[0]['name'])
def get_delim_text(soup):
	text = soup.get_text()
	# break into lines and remove leading and trailing space on each
	lines = (line.strip() for line in text.splitlines())
	# break multi-headlines into a line each
	chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
	# drop blank lines
	text = '\n'.join(chunk for chunk in chunks if chunk)
	return text

from html.parser import HTMLParser

from html.parser import HTMLParser
from html.entities import name2codepoint

class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        print("Start tag:", tag)
        for attr in attrs:
            print("     attr:", attr)
    def handle_endtag(self, tag):
        print("End tag  :", tag)
    def handle_data(self, data):
        print("Data     :", data)
    def handle_comment(self, data):
        print("Comment  :", data)
    def handle_entityref(self, name):
        c = chr(name2codepoint[name])
        print("Named ent:", c)
    def handle_charref(self, name):
        if name.startswith('x'):
            c = chr(int(name[1:], 16))
        else:
            c = chr(int(name))
        print("Num ent  :", c)
    def handle_decl(self, data):
        print("Decl     :", data)

soup = BeautifulSoup (open("form10k.htm"),'lxml')
# parser = MyHTMLParser()
# parser.feed(soup.prettify())



content = soup.prettify()
links = soup.find_all("a",href=False)
names = [link['name'] for link in links]
name = names[2]

print(name)
begin = content.find(name)
end = content.rfind(name)
print(begin,end+len(name))



a = BeautifulSoup(content[begin:end],'lxml')
print(content[begin:end])
# with open("try.xml","w") as xml:
	# xml.write(content[begin:end])


# print(get_delim_text(a))



exit()



counts = [content.count(name) for name in names]

print(counts)
print(names)

# result = re.findall("PART I.*?PART II", content, flags=re.S)
# print(result)
# print(result.group(0))







