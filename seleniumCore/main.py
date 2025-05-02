import os
import time
import functions
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait  
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Setup WebDriver
service = Service("/usr/local/bin/chromedriver")
driver = webdriver.Chrome(service=service)

#get the main page
originalUrl = "https://gaokao.eol.cn/e_html/gk/gkst/2023st.shtml"
driver.get(originalUrl)


# nationalA:st1/nationalB: st2/BEIJING:st5/TIANJIN:st6/ZHEJIANG:st7

examTypes = ["nationalA", "nationalB", "Beijing", "Tianjin","ZHEJIANG"]
# i need to make a python server that connects to postgresql and fetch data



nationalAContainer = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,"//div[@id='st1'" )))


'''
nationalBContainer = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,"//div[@id='st2'" )))
BeijingContainer = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,"//div[@id='st5'" )))
TianjinContainer = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,"//div[@id='st6'" )))
zhejiangContainer = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,"//div[@id='st6'" )))


'''

# national_A_container = driver.


