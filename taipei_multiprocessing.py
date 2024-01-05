import json
from tool import find_lat_lon, within_distance
import time
import os
from multiprocessing import Pool

import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup as Soup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

coordinate = [(25.0371, 121.566), (25.0474, 121.572)]

options = Options()
service = Service()
options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--lang=en-US")
options.add_experimental_option("prefs", {"intl.accept_languages": "en"})
driver = webdriver.Chrome(service=service, options=options)


def scrape_data(ty):
    file_path = f"data/taipei_{ty}.json"
    if os.path.exists(file_path):
        with open(file_path) as f:
            data = json.load(f)
    else:
        data = {}

    place_set = set()
    for point in coordinate:
        lat = point[0]
        lon = point[1]

        place_name = []

        __url = f"https://www.google.com/maps/search/{ty}/@{lat},{lon},16z/data=!3m1!4b1!4m6!2m5!3m4!2s{lat},+{lon}!4m2!1d{lon}!2d{lat}?hl=en?entry=ttu"
        driver.get(__url)
        start = time.time()
        processing = 0
        while processing <= 150:
            try:
                element = driver.find_element(By.CSS_SELECTOR, '.lXJj5c.Hk4XGb')
                driver.execute_script("arguments[0].scrollIntoView();", element)
                time.sleep(2.5 if processing > 70 else 1.5)
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

    for info in place_set:
        place_name.append({"name": info[0], "a": info[1], "keyword": info[2], 'category': info[3], "lat": info[4], "lon": info[5]})

    data[ty] = place_name

    with open(file_path, "w") as f:
        json.dump(data, f)

    print(f"Type: {ty} finished")

if __name__ == "__main__":
    
    genres = ["library", "store", "gym", "park", "city+hall", "school"]

    with Pool(processes=len(genres)) as pool:
        pool.map(scrape_data, genres)

    driver.quit()
