from bs4 import BeautifulSoup
import requests
import urllib
import re
# from html.parser import HTMLParser
# from html.entities import name2codepoint
import pandas as pd
import numpy as np

def get_urls(url):
	soup = BeautifulSoup(requests.get(url).text,'lxml')
	return [link.get('href') for  link in soup.find_all('a') if link.get('href').startswith('/Archives/edgar/data/')] # COMMON_PREFIX = '/Archives/edgar/data/'

def get_delim_text(soup):
	text = soup.get_text()
	# break into lines and remove leading and trailing space on each
	lines = (line.strip() for line in text.splitlines())
	# break multi-headlines into a line each
	chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
	# drop blank lines
	text = '\n'.join(chunk for chunk in chunks if chunk)
	return text


def get_dict(keys,values):
    look_up = {}
    for i in range(len(keys)):
        look_up[keys[i]] = values[i]
    return look_up

def get_link(soup,item_number,item_name=None):

    item_numbers = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
    item_names=["Business","Properties","Legal Proceedings","Mine Safety Disclosures","Market for Registrant’s Common Equity, Related Stockholder Matters and Issuer Purchases of Equity Securities",
                "Selected Financial Data","Management’s Discussion and Analysis of Financial Condition and Results of Operations",
                "Financial Statements and Supplementary Data","Changes in and Disagreements With Accountants on Accounting and Financial Disclosure",
                "Directors, Executive Officers and Corporate Governance","Executive Compensation","Security Ownership of Certain Beneficial Owners and Management and Related Stockholder Matters",
                "Certain Relationships and Related Transactions, and Director Independence",
                "Principal Accountant Fees and Services",
                "Exhibits, Financial Statement Schedules",
                "Form 10-K Summary"]

    look_up =  get_dict(item_numbers,item_names)

    index_name = "Item {}\\.".format(int(item_number))
    item_name = look_up[(item_number)]
    
    regexp = re.compile(index_name)
    regexp_name = re.compile(item_name)

    tags = soup.find_all('a')
    target_tags = [tag for tag in tags if regexp.match(tag.get_text().strip())  or regexp_name.match(tag.get_text().strip())]
    links = [t.get('href') for t in target_tags]
    link = np.unique(links)[0]
    return link

def get_tags(soup,link,direction='after'):
    if link.startswith("#"):
        link = link[1:]
    tags = soup.find_all(lambda tag: tag.name == 'a' and tag.get('name') )#and tag.text)
    # tags = [ tag for tag in soup.find_all('a') if tag.get('name') and  tag.text]
    target_tags = [tag for tag in tags if tag.get('name')==link]
    tag = (list(target_tags))[0]

    if direction.upper()=='AFTER':
        tags = tag.find_all_next()
    elif direction.upper()=='BEFORE':
        tags = tag.find_all_previous()
    else:
        print("Invalid input.")
        tags = None
    return tags

def get_item_tags(soup,item_number,item_name=None):

    begin_link = get_link(soup,item_number,item_name)
    end_link = get_link(soup,item_number+1)

    after_begin_tags = get_tags(soup,begin_link,'after')
    before_end_tags = get_tags(soup,end_link,'before')

    def is_useful(tag):
        return not (tag.is_empty_element or tag.name =='td' or tag.text == '\n')
    after_ = [a for a in after_begin_tags if is_useful(a)]
    before_ = [b for b in before_end_tags if is_useful(b)]

    result_ = set(before_).intersection(set(after_))
    return result_ , begin_link

# much slower than list comprehension, for reference only
def clean(tagset):
    extract = lambda tag: (not tag.is_empty_element and not tag.name=='td')
    result = filter(extract,tagset)
    return set(result)

# not implemented yet
def get_text(soup,item_number,item_name=None):
    begin_link = get_link(item_name,item_name)
    end_link = get_link(item_number+1)
    marks = soup.find_all(lambda tag: tag.name == 'a' and tag.get('name') and tag.text)
    # get text from begin to end
    begin_tag = begin_link[1:]
    end_tag = end_link[1:]
    return

def open_page(file,link):
    import os
    path = (os.path.abspath(file)+link)
    import webbrowser as wb
    wb.open_new_tab(path)

def get_soup_without_table(filename):
    soup = BeautifulSoup (open(filename),'lxml')
    # remove tables from in Item 1 onwards:
    link = get_link(soup,1)
    tags = get_tags(soup,link,'after')
    for tag in tags:
        if tag.name == 'table':
            tag.extract()
    return soup


def get_text(filename,item_number,write_to_file=False,open_in_new_tab=False):
    soup = get_soup_without_table(filename)   
    tags , link = get_item_tags(soup, item_number)
    text = "".join([ r.text.strip()+"\n" for r in tags]   ) 
    text = "\n".join((line.strip() for line in text.splitlines()))
    text = "Item {}.\n{}".format(str(item_number),text)
    if write_to_file:
        with open("Item {} text".format(str(item_number)),'w', encoding='utf-8') as w:
            w.write(text)
    if open_in_new_tab:
        open_page(filename,link)
    return text

# soup = BeautifulSoup (open("form10k.htm"),'lxml')
# url = "https://www.sec.gov/Archives/edgar/data/1652044/000165204418000007/goog10-kq42017.htm"
# url = "http://investor.apple.com/secfiling.cfm?filingid=320193-17-70&cik=320193#A10-K20179302017_HTM_SDAFBE4E1E0DC4B1F8BDB4EB2D4449AFA"
# url = "http://investor.apple.com/secfiling.cfm?filingid=320193-17-70&cik=320193"  # apple url

# ***********************************************************************************************************************    
# DO NOT edit above code


# ___ main starts here ____

if __name__ == '__main__':

    filepath = "sec1.htm"
    item_number = 7
    write_to_file = True  # overwrites a file names: "Item {} text", e.g. Item 7 text
    open_in_new_tab = False # opens up the default browser and displays the target Item

    # table is NOT captured
    # text is captured, but the order is NOT completely correct
    text = get_text(filepath, item_number ,write_to_file, open_in_new_tab)

    exit()