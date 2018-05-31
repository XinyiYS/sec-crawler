
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os



path = os.path.join(os.getcwd(), 'chromedriver')  # this is for mac users

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')

driver = webdriver.Chrome(chrome_options=chrome_options,executable_path=path)


# driver = webdriver.Chrome('./chromedriver_win32/chromedriver.exe')#windows


