import json
from tool import find_lat_lon, within_distance
import time
import os
from multiprocessing import Pool, cpu_count

from selenium import webdriver
from bs4 import BeautifulSoup as Soup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

import logging

logger = logging.getLogger("google_crawler_logger")
logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)

with open('Taipei_Point_500m_lat_lon.geojson') as f:
    coordinates = json.load(f)['features']

# coordinate = [(25.0371, 121.566), (25.0474, 121.572)]

a1 = time.time()

options = Options()
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--lang=en-US")
options.add_experimental_option("prefs", {"intl.accept_languages": "en"})
options.binary_location = '/usr/bin/google-chrome'

def scrape_data(ty):

    a2 = time.time()

    place_set = set()
    file_path = f"taipei/{ty}.json"
    if os.path.exists(file_path):
        with open(file_path) as f:
            data = json.load(f)
    else:
        data = {'check_point': -1}
    
    if data['check_point'] >= 0:
        for info in data[ty]:
            place_set.add((info['name'], info['a'], info['keyword'], info['category'], info['lat'], info['lon'], info['address'], info['star'], info['comments']))
        logger.debug(f">> {ty} Started from point {data['check_point']+1}")
    elif data['check_point'] == -2:
        logger.debug(f"Type: {ty} Skipped")
        return
    else:
        logger.debug(f">> {ty} Started from point 0")
    error_point = []
    for idx, point in enumerate(coordinates):
        try:
            if idx <= data['check_point']:
                continue
            lat = point['geometry']['coordinates'][1]
            lon = point['geometry']['coordinates'][0]

            # lat = 42.3611444
            # lon = -71.1023658

            service = Service()
            driver = webdriver.Chrome(service=service, options=options)

            place_name = []
            __url = f"https://www.google.com/maps/search/{ty}/@{lat},{lon},16z/data=!3m1!4b1!4m6!2m5!3m4!2s{lat},+{lon}!4m2!1d{lon}!2d{lat}?hl=en?entry=ttu"
            driver.get(__url)
            start = time.time()
            processing = 0
            prev_data_length = 0
            while processing <= 100:
                content = driver.page_source
                tmp_soup = Soup(content, "html.parser")
                tmp_divs = tmp_soup.find_all(class_="TFQHme")
                data_length = len(tmp_divs)
                time.sleep(0.1)
                # logger.debug(prev_data_length, data_length)
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
            driver.quit()
            soup = Soup(content, "html.parser")
            divs = soup.find_all(class_="qBF1Pd fontHeadlineSmall")
            arefs = soup.find_all(class_="hfpxzc")
            category = soup.find_all(class_="W4Efsd")
            review = soup.find_all(class_="e4rVHe fontBodyMedium")
            categories = []
            addresses = []
            comment = []
            for outer_div in category:
                inner_div = outer_div.find('div', class_='W4Efsd')
                if inner_div is not None:
                    span_text = inner_div.find_all('span')
                    categories.append(span_text[0].text)
                    addresses.append(span_text[-1].text if span_text[-1].text!=span_text[0].text else "")

            if review != []:
                for outer_span in review:
                    inner_div = outer_span.find('span', class_='ZkP5Je')
                    if inner_div is not None:
                        star = outer_span.find('span', class_='MW4etd')
                        reviews = outer_span.find('span', class_='UY7F9')
                        comment.append([float(star.text), int(reviews.text[1:-1].replace(",", ""))])
                    else:
                        comment.append(["", ""])
            else:
                comment = [["", ""]] * len(categories)
                    
            for i, r in enumerate(zip(divs, arefs)):
                href = str(r[1].get('href'))
                lat2, lon2 = find_lat_lon(href)
                if lat2 is not None:
                    if within_distance(lat1=lat, lon1=lon, lat2=lat2, lon2=lon2, max_distance=600):
                        place_set.add((r[0].text, href, ty, categories[i], lat2, lon2, addresses[i], comment[i][0], comment[i][1]))
            
            if idx % 5 == 0:
                for info in place_set:
                    place_name.append({"name": info[0], "a": info[1], "keyword": info[2], 'category': info[3], "lat": info[4], "lon": info[5], "address": info[6], "star": info[7], "comments": info[8]})
                
                data[ty] = place_name
                data["check_point"] = idx
                data["error"] = error_point

                with open(file_path, "w") as f:
                    json.dump(data, f)
            
            if idx % 100 == 0 and idx != 0:
                logger.debug(f">> {ty} - {idx}/{len(coordinates)} | Time: {round(time.time() - a1, 2)}")
        except Exception as e:
            logger.debug(f"Error Messages: {e}")
            error_point.append(idx)

    for info in place_set:
        # logger.debug(info)
        place_name.append({"name": info[0], "a": info[1], "keyword": info[2], 'category': info[3], "lat": info[4], "lon": info[5], "address": info[6], "star": info[7], "comments": info[8]})

    data[ty] = place_name
    data["check_point"] = -2
    data["error"] = error_point

    with open(file_path, "w") as f:
        json.dump(data, f)

    logger.debug(f"Type: {ty} finished | Processing: {round(time.time() - a2, 2)} | Total: {round(time.time() - a1, 2)}")

if __name__ == "__main__":
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
    
    num_cores = int(cpu_count()*0.5)
    logger.debug(f"{'-'*15} CPU Count: {num_cores} {'-'*15}")
    with Pool(num_cores) as pool:
        for ty in genres:
            pool.apply_async(
                scrape_data,
                (ty,)
            )
        pool.close()
        pool.join()