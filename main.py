import os
import re
import time
import pandas as pd
import json
import csv
from datetime import datetime
from selenium import webdriver
from bs4 import BeautifulSoup as Soup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import WebDriverException

# print(1)
# myProxy = "50.168.72.119:80"
# proxy = Proxy({
#     'proxyType': ProxyType.MANUAL,
#     'httpProxy': myProxy,
#     'sslProxy': myProxy,
#     'noProxy': ''})

# Configure capabilities 
# capabilities = webdriver.DesiredCapabilities.CHROME

# options.proxy = proxy
# proxy.to_capabilities()

options = Options()

service = Service()

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--lang=en-US")
options.add_experimental_option("prefs", {"intl.accept_languages": "en"})

driver = webdriver.Chrome(service=service, options=options)

# driver.get("https://google.com/")
# print(driver.title)
# driver.quit()

place_name = []
genres = [
    "school",
    "subway_station", # https://www.google.com/maps/search/subway+station/@25.0368238,121.5306812,14z/data=!3m1!4b1!4m6!2m5!3m4!2s25.0374,+121.5439!4m2!1d121.5438779!2d25.037431?entry=ttu
    # "subway_station",
    "university",
    "shopping_mall",
    "local_government_office", # https://www.google.com/maps/search/government/@25.0369736,121.5306812,14z/data=!3m1!4b1!4m6!2m5!3m4!2s25.0374,+121.5439!4m2!1d121.5438779!2d25.037431?entry=ttu
    # "city_hall",
]

# __test_url = f"https://www.google.com/maps/search/school/@25.0366825,121.546131,16z/data=!4m6!2m5!3m4!2s25.0407,+121.5486!4m2!1d121.5486371!2d25.0407356?entry=ttu"
# # __school_url = f"https://www.google.com/maps/search/{ty}/@{lat},{lon},16z/data=!3m1!4b1!4m6!2m5!3m4!2s{lat},+{lon}!4m2!1d{lon}!2d{lat}?hl=en?entry=ttu"
# driver.get(__test_url)
# content = driver.page_source
# soup = Soup(content,"lxml")
# divs = soup.find_all(class_="qBF1Pd fontHeadlineSmall")
# arefs = soup.find_all(class_="hfpxzc")
# # place_name += [{"div": r[0].text, "a": str(r[1]), "type": ty} for r in zip(divs, arefs)]
# print(divs)

with open("parking_test.json") as f:
    data = json.load(f)

with open("parking_name_ls.json", "r") as f:
    pk = json.load(f)["name"]

# cache 
df = pd.read_csv('./parking_memo2.csv', header=None, names=['name'], dtype='str')
cache_name = df[df.columns[0]].tolist()

# print(len(set(cache_name)) == len(cache_name))
# assert pk[0]['res'] in cache_name, "cache_name is not in pk"

# exit()

# while len(set(cache_name)) <= len(pk):
#     try:

for p in pk:
    if p['res'] in cache_name:
        print('pass ', p['res'])
        continue

    p_name = p["res"]
    lat = p["lat"]  # 20
    lon = p["lon"]  # 120
    tmp = {p_name: None}

    place_name = []

    for ty in genres:
        # __school_url = f"https://www.google.com/maps/search/school/@{lat},{lon},16z/data=!3m1!4b1!4m6!2m5!3m4!2s{lat},+{lon}!4m2!1d{lon}!2d{lat}?hl=en?entry=ttu"
        # __test_url = f"https://www.google.com/maps/search/school/@25.0366825,121.546131,16z/data=!4m6!2m5!3m4!2s25.0407,+121.5486!4m2!1d121.5486371!2d25.0407356?entry=ttu"
        __school_url = f"https://www.google.com/maps/search/{ty}/@{lat},{lon},16z/data=!3m1!4b1!4m6!2m5!3m4!2s{lat},+{lon}!4m2!1d{lon}!2d{lat}?hl=en?entry=ttu"
        driver.get(__school_url)
        content = driver.page_source
        soup = Soup(content, "lxml")
        divs = soup.find_all(class_="qBF1Pd fontHeadlineSmall")
        arefs = soup.find_all(class_="hfpxzc")
        place_name += [
            {"div": r[0].text, "a": str(r[1]), "type": ty} for r in zip(divs, arefs)
        ]

    tmp[p_name] = place_name

    data.update(tmp)

    # print(place_name)

    with open("parking_test.json", "w") as f:
        json.dump(data, f)

    with open("parking_memo.csv", "a") as f:
        # create the csv writer
        writer = csv.writer(f)
        # write a row to the csv file
        writer.writerow([p_name])

    print(f"parking station {p_name} finished")
    
    # except WebDriverException as e:
    #     print(e)
    #     # driver.quit()
    #     # driver = webdriver.Chrome(service=service, options=options)
    #     continue


driver.quit()
