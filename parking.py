import json 
from tool import find_lat_lon, within_distance
import time

# pre process
with open ("parking/parking_name_ls.json", "r") as f:
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
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

options = Options()

service = Service()

options = webdriver.ChromeOptions()
# options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--lang=en-US")
options.add_experimental_option("prefs", {"intl.accept_languages": "en"})

driver = webdriver.Chrome(service=service, options=options)

place_name = []
genres = [
    "accounting", "airport", "amusement+park", "aquarium", "art+gallery", "atm", "bakery", "bank",
    "bar", "beauty+salon", "bicycle+store", "book+store", "bowling+alley", "bus+station", "cafe", "campground",
    "car+dealer", "car+rental", "car+repair", "car+wash", "casino", "cemetery", "church", "city+hall",
    "clothing+store", "convenience+store", "courthouse", "dentist", "department+store", "doctor", "drugstore", "electrician",
    "electronics+store", "embassy", "fire+station", "florist", "funeral+home", "furniture+store", "gas+station", "gym",
    "hair+care", "hardware+store", "hindu+temple", "home+goods+store", "hospital", "insurance+agency", "jewelry+store", "laundry",
    "lawyer", "library", "light+rail+station", "liquor+store", "local+government+office", "locksmith", "lodging", "meal+delivery",
    "meal+takeaway", "mosque", "movie+rental", "movie+theater", "moving+company", "museum", "night+club", "painter", "park",
    "parking", "pet+store", "pharmacy", "physiotherapist", "plumber", "police", "post+office", "primary+school", "real+estate+agency",
    "restaurant", "roofing+contractor", "rv+park", "school", "secondary+school", "shoe+store", "shopping+mall", "spa", "stadium",
    "storage", "store", "subway+station", "supermarket", "synagogue", "taxi+stand", "tourist+attraction", "train+station", "transit+station",
    "travel+agency", "university", "veterinary+care", "zoo"
]


with open("parking/parking_test.json") as f:
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

    # if p_name == "民生社區中心地下停車場":

    for idx, ty in enumerate(genres):
        __url = f"https://www.google.com/maps/search/{ty}/@{lat},{lon},16z/data=!3m1!4b1!4m6!2m5!3m4!2s{lat},+{lon}!4m2!1d{lon}!2d{lat}?hl=en?entry=ttu"
        print(__url)
        # __url = "https://www.google.com/maps/search/accounting/@25.0411595,121.5528998,16z/data=!3m1!4b1!4m6!2m5!3m4!2s25.039,+121.5671!4m2!1d121.5670602!2d25.039018?authuser=0&entry=ttu"
        driver.get(__url)
        # time.sleep(10000)
        start = time.time()
        while time.time() - start <= 120:
            try:
                element = driver.find_element(By.CSS_SELECTOR, '.lXJj5c.Hk4XGb')
                driver.execute_script("arguments[0].scrollIntoView();", element)
                time.sleep(1.5)
            except:
                element = driver.find_element(By.CSS_SELECTOR, '.HlvSq')
                driver.execute_script("arguments[0].scrollIntoView();", element)
                break
        content = driver.page_source
        soup = Soup(content, "html.parser")
        divs = soup.find_all(class_="qBF1Pd fontHeadlineSmall")
        arefs = soup.find_all(class_="hfpxzc")
        category = soup.find_all(class_="W4Efsd")
        categories = []
        for outer_div in category:
            inner_div = outer_div.find('div', class_='W4Efsd')
            if inner_div:
                span_text = inner_div.find('span').text
                categories.append(span_text)
        print(len(arefs), len(categories))
        for i, r in enumerate(zip(divs, arefs)):
            href = str(r[1].get('href'))
            lat2, lon2 = find_lat_lon(href)
            if lat2 is not None:
                if within_distance(lat1=lat, lon1=lon, lat2=lat2, lon2=lon2, max_distance=350):
                    # TODO: Add lat, lon and others. 
                    place_name.append({"div": r[0].text, "a": str(r[1]), "keyword": ty, 'category': categories[i],})

    tmp[p_name] = place_name

    data.update(tmp)

    with open("parking/parking_test.json", "w") as f:
        json.dump(data, f)

    with open("parking/parking_memo.csv", "a") as f:
        writer = csv.writer(f)
        writer.writerow([p_name])

    print(f"parking station {p_name} finished")

driver.quit()
