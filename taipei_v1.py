import json 
from tool import find_lat_lon, within_distance
import time

import os
import json
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

genres = ["library", "store", "park", "city+hall", "school", "airport", "zoo", "university", "book+store", "night+club", "parking"]

# genres = ["store"]

with open('Taipei_point_100m_lat_lon.geojson') as f:
    coordinates = json.load(f)['features']
    
a1 =  time.time()

for ty in genres:
    a2 = time.time()
    file_path = f"taipei/{ty}.json"
    if os.path.exists(file_path):
        with open(file_path) as f:
            data = json.load(f)
    else:
        data = {}

    place_set = set()

    for i, point in enumerate(coordinates):
        lat = point['geometry']['coordinates'][1]
        lon = point['geometry']['coordinates'][0]

        place_name = []

        __url = f"https://www.google.com/maps/search/{ty}/@{lat},{lon},16z/data=!3m1!4b1!4m6!2m5!3m4!2s{lat},+{lon}!4m2!1d{lon}!2d{lat}?hl=en?entry=ttu"
        # __url = "https://www.google.com/maps/search/%E9%A4%90%E5%BB%B3/@24.9682597,121.4258838,15z/data=!4m2!2m1!6e5?authuser=0&entry=ttu"
        print(__url)
        driver.get(__url)
        start = time.time()
        processing = 0
        prev_data_length = 0
        while processing <= 40:
            content = driver.page_source
            tmp_soup = Soup(content, "html.parser")
            tmp_divs = tmp_soup.find_all(class_="TFQHme")
            data_length = len(tmp_divs)
            time.sleep(0.1)
            # print(prev_data_length, data_length)
            try:
                if data_length != prev_data_length:
                    element = driver.find_element(By.CSS_SELECTOR, '.lXJj5c.Hk4XGb')
                    driver.execute_script("arguments[0].scrollIntoView();", element)
                    prev_data_length = data_length
                    start = time.time()
                else:
                    try:
                        element = driver.find_element(By.CSS_SELECTOR, '.HlvSq')
                        driver.execute_script("arguments[0].scrollIntoView();", element)
                        break
                    except:
                        pass
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
                span_text = inner_div.find_all('span')
                if len(span_text) == 2:
                    categories.append([])
                else:
                    categories.append(span_text[0].text)
                
        for i, r in enumerate(zip(divs, arefs)):
            href = str(r[1].get('href'))
            lat2, lon2 = find_lat_lon(href)
            if lat2 is not None:
                if categories[i] != []:
                    if within_distance(lat1=lat, lon1=lon, lat2=lat2, lon2=lon2, max_distance=350):
                        place_set.add((r[0].text, href, ty, categories[i], lat2, lon2))
                    # place_name.append({"name": r[0].text, "a": href, "keyword": ty, 'category': categories[i], "lat": lat2, "lon": lon2})

    for info in place_set:
        place_name.append({"name": info[0], "a": info[1], "keyword": info[2], 'category': info[3], "lat": info[4], "lon": info[5]})

    data[ty] = place_name

    with open(file_path, "w") as f:
        json.dump(data, f)

    print(f"Type: {ty} finished | Processing: {time.time() - a2} | Total: {time.time() - a1}")

driver.quit()
