import json 
from tool import find_lat_lon, within_distance
import time
    
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

genres = [
    "library", "store", "gym", "park", "city+hall", "school"
]


with open("taipei_place.json") as f:
    data = json.load(f)

coordinate = [(25.0371, 121.566), (25.0474, 121.572)]

# df = pd.read_csv('./parking_memo2.csv', header=None, names=['name'], dtype='str')
# cache_name = df[df.columns[0]].tolist()

for ty in genres:
    place_set = set()
    tmp = {ty: None}

    for point in coordinate:
        lat = point[0]  # 20
        lon = point[1]  # 120

        place_name = []

        __url = f"https://www.google.com/maps/search/{ty}/@{lat},{lon},16z/data=!3m1!4b1!4m6!2m5!3m4!2s{lat},+{lon}!4m2!1d{lon}!2d{lat}?hl=en?entry=ttu"
        driver.get(__url)
        start = time.time()
        processing = 0
        while processing <= 120:
            try:
                element = driver.find_element(By.CSS_SELECTOR, '.lXJj5c.Hk4XGb')
                driver.execute_script("arguments[0].scrollIntoView();", element)
                time.sleep(2 if processing > 70 else 1.3)
            except:
                element = driver.find_element(By.CSS_SELECTOR, '.HlvSq')
                driver.execute_script("arguments[0].scrollIntoView();", element)
                break
            processing = time.time()-start

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
        for i, r in enumerate(zip(divs, arefs)):
            href = str(r[1].get('href'))
            lat2, lon2 = find_lat_lon(href)
            if lat2 is not None:
                if within_distance(lat1=lat, lon1=lon, lat2=lat2, lon2=lon2, max_distance=350):
                    place_set.add((r[0].text, href, ty, categories[i], lat2, lon2))
                    # place_name.append({"name": r[0].text, "a": href, "keyword": ty, 'category': categories[i], "lat": lat2, "lon": lon2})

    for info in place_set:
        place_name.append({"name": info[0], "a": info[1], "keyword": info[2], 'category': info[3], "lat": info[4], "lon": info[5]})

    data[ty] = place_name

    with open("taipei_place.json", "w") as f:
        json.dump(data, f)

    print(f"Type: {ty} finished")

driver.quit()
