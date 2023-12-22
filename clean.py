import json 

# pre process
with open ("parking_name_ls.json", "r") as f:
    data = json.load(f)['name']
    
n_set = set()
clean_ls = []

for i in data:
    if i['res'] not in n_set:
        clean_ls.append(i)
        n_set.add(i['res'])

    elif i['lat'] / 24 <= 1 or i['lon'] / 120 <= 1:
        continue
        
    else:
        continue
    
import pandas as pd
import json
import csv
from selenium import webdriver
from bs4 import BeautifulSoup as Soup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

options = Options()

service = Service()

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--lang=en-US")
options.add_experimental_option("prefs", {"intl.accept_languages": "en"})

driver = webdriver.Chrome(service=service, options=options)

place_name = []
genres = [
    "school",
    "subway+station",
    "university",
    "shopping+mall",
    "government",
]

with open("parking_test.json") as f:
    data = json.load(f)

df = pd.read_csv('./parking_memo2.csv', header=None, names=['name'], dtype='str')
cache_name = df[df.columns[0]].tolist()

for p in clean_ls:
    if p['res'] in cache_name:
        print('pass ', p['res'])
        continue

    p_name = p["res"]
    lat = p["lat"]  # 20
    lon = p["lon"]  # 120
    tmp = {p_name: None}

    place_name = []

    for ty in genres:
        __url = f"https://www.google.com/maps/search/{ty}/@{lat},{lon},16z/data=!3m1!4b1!4m6!2m5!3m4!2s{lat},+{lon}!4m2!1d{lon}!2d{lat}?hl=en?entry=ttu"
        driver.get(__url)
        content = driver.page_source
        soup = Soup(content, "lxml")
        divs = soup.find_all(class_="qBF1Pd fontHeadlineSmall")
        arefs = soup.find_all(class_="hfpxzc")
        place_name += [
            {"div": r[0].text, "a": str(r[1]), "type": ty} for r in zip(divs, arefs)
        ]

    tmp[p_name] = place_name

    data.update(tmp)

    with open("parking_test.json", "w") as f:
        json.dump(data, f)

    with open("parking_memo.csv", "a") as f:
        writer = csv.writer(f)
        writer.writerow([p_name])

    print(f"parking station {p_name} finished")

driver.quit()