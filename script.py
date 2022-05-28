import sys
import time
import csv

import requests

from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# CONST
base_url            = "https://www.tokopedia.com/p/handphone-tablet/handphone"
paging              = "?page="
inv_attr            = {'class':'css-bk6tzz e1nlzfl2'}
inv_url_attr        = {'class': 'css-89jnbj'}
name_attr           = {'class':'css-1bjwylw'}
desc_attr           = {'class':'css-1dmo88g'}
image_attr          = {'class':'css-1c345mg'}
price_attr          = {'class':'css-o5uqvq'}
rating_attr         = {'class':'css-153qjw7'}
rating_src          = {'src':'https://assets.tokopedia.net/assets-tokopedia-lite/v2/zeus/kratos/4fede911.svg'}
merchant_attr       = {'class':'css-vbihp9'}
merchant_span_attr  = {'class':'css-1kr22w3'}
topads_attr         = {'alt': 'topads icon'}
user_agent          = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0'  
max_inventory_count = 100

class Inventory:
    def __init__(self, name, desc, image, price, rating, merchant):
        self.name = name
        self.desc = desc
        self.image = image
        self.price = price
        self.rating = rating
        self.merchant = merchant
    
    def print(self):
        print(self.name, self.desc, self.image, self.price, self.rating, self.merchant)
    
    def toCsvFormat(self):
        return [self.name, self.desc, self.image, self.price, self.rating, self.merchant]

# Config for headless
def generateSeleniumOptions():
    options = Options()
    options.headless = True
    options.add_argument('--no-sandbox') # Bypass OS security model
    options.add_argument('start-maximized')
    options.add_argument('disable-infobars')
    options.add_argument("--disable-extensions")
    options.add_argument('user-agent={0}'.format(user_agent))
    options.add_argument('--log-level=3')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    return options

# Scrolling function
def scroll(driver):
    time.sleep(1)
    elem = driver.find_element(by=By.TAG_NAME, value="body")
    elem.send_keys(Keys.PAGE_DOWN)
    time.sleep(0.2)
    elem.send_keys(Keys.PAGE_DOWN)
    time.sleep(0.2)
    elem.send_keys(Keys.PAGE_DOWN)
    time.sleep(0.2)
    elem.send_keys(Keys.PAGE_DOWN)
    time.sleep(0.2)
    elem.send_keys(Keys.PAGE_DOWN)
    time.sleep(0.2)
    elem.send_keys(Keys.PAGE_DOWN)
    time.sleep(2)

def scraper():
    start_time = time.time()
    f = open('data.csv', 'w', newline='') # Open file and write to Csv Library
    writer = csv.writer(f)
    writer.writerow(["Name of Product", "Description", "Image Link", "Price", "Rating", "Merchant"]) # CSV Header
    count = 0 # Counter for inventory, start from 0

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=generateSeleniumOptions())
    for i in range (1,3): # Limit only to two pages, because we only need top 100 product
        url = f"{base_url}{paging}{i}" # Define url for current page
        # Open url via chrome browser and scroll to show all inventories
        driver.get(url)
        scroll(driver)

        # Parse page to BeautifulSoup lib
        content = driver.page_source
        soup = bs(content, features="html.parser")
        for item in soup.find_all('div', attrs=inv_attr): # Loop for every inventory in the page
            if count == max_inventory_count: # Stop the looping if inventory has reached max_inventory_count
                break
            #Ignoring topads product
            if isTopAds(item):
                continue

            desc, img = getDescAndImage(driver, item)
            inventory = Inventory(
                getName(item),
                desc,
                img,
                getPrice(item),
                getRating(item),
                getMerchant(item)
            )
            writer.writerow(inventory.toCsvFormat()) # Write inventory into csv
            count+=1
            printProgress(count)
    # Print time
    print(f"\nFinished after {(time.time() - start_time):.2f}s")
    # Close all stream after finished
    f.close()
    driver.quit()

# Function to check if the product is topads
def isTopAds(item):
    topads = item.find('img', attrs=topads_attr)
    return topads != None
            
# Function to fetch name of product
def getName(item):
    name = item.find('span', attrs=name_attr)
    return name.text

# Function to fetch description of product
def getDescAndImage(driver, item):
    url_to_inv_page = item.find('a', attrs=inv_url_attr)['href']
    driver.get(url_to_inv_page)
    time.sleep(1)
    content = driver.page_source
    soup = bs(content, features="html.parser")
    desc_list = []
    for desc in soup.find_all('li', attrs=desc_attr):
        span_list = desc.find_all('span')
        title = str(span_list[0].text).strip().replace('<!---->','')
        if len(span_list) == 2:
            value = str(span_list[1].text).strip()
            desc_list.append(f"{title}{value}")
        else:
            value = str(desc.find('a').text).strip().replace('<b>','').replace('</b>','')
            desc_list.append(f"{title}{value}")
    
    # Fetching Image
    image = soup.find('img', attrs=image_attr)
    return ', '.join(desc_list), image['src']

# Function to fetch price of product
def getPrice(item):
    price = item.find('span', attrs=price_attr)
    return price.text

# Function to fetch rating of product
def getRating(item):
    rating = item.find('div', attrs=rating_attr)
    if rating != None:        
        return len(rating.find_all('img', attrs=rating_src))
    else:
        return 0

# Function to fetch merchant name
def getMerchant(item):
    merchant_div = item.find('div', attrs=merchant_attr)
    merchant_list = merchant_div.find_all('span', attrs=merchant_span_attr)
    if len(merchant_list) == 2:
        return merchant_list[1].text
    else:
        return "No Merchant Name"

# Print progress to terminal
def printProgress(i):
    currentPercentage = (i/max_inventory_count)*100
    print(f"\rFetching...\t\t{i} products\t\t[{currentPercentage:.2f}%]", end="")


# Start script
scraper()