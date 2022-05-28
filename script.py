import sys
import time
import csv

import requests

from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# CONST
base_url = "https://www.tokopedia.com/p/handphone-tablet/handphone"
paging = "?page="
inv_attr = {'class':'css-bk6tzz e1nlzfl2'}
name_attr = {'class':'css-1bjwylw'}
image_attr = {'class':'css-1c0vu8l'}
price_attr = {'class':'css-o5uqvq'}
rating_attr = {'class':'css-153qjw7'}
rating_src = {'src':'https://assets.tokopedia.net/assets-tokopedia-lite/v2/zeus/kratos/4fede911.svg'}
merchant_attr = {'class':'css-vbihp9'}
merchant_span_attr = {'class':'css-1kr22w3'}
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
    time.sleep(1)

def scraper():
    f = open('data.csv', 'w', newline='') # Open file and write to Csv Library
    writer = csv.writer(f)
    writer.writerow(["Name of Product", "Description", "Image Link", "Price", "Rating", "Merchant"]) # CSV Header
    count = 0 # Counter for inventory, start from 0

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    for i in range (1,3):
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
            inventory = Inventory(
                getName(item),
                "",
                getImage(item),
                getPrice(item),
                getRating(item),
                getMerchant(item)
            )
            writer.writerow(inventory.toCsvFormat()) # Write inventory into csv
            count+=1
    # Close all stream after finished
    f.close()
    driver.quit()
            
# Function to fetch name of product
def getName(item):
    name = item.find('span', attrs=name_attr)
    return name.text

# Function to fetch description of product
def getDesc(item):
    name = item.find('span', attrs=name_attr)

    return name.text

# Function to fetch image link of product
def getImage(item):
    image_div = item.find('div', attrs=image_attr)
    image = item.find('img')
    return image['src']

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


# Start script
scraper()