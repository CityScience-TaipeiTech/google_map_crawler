import json
from tool import find_lat_lon, within_distance
import time
import os

from selenium import webdriver
from bs4 import BeautifulSoup as Soup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

def scrape_data(category: str, save_path: str, target_area: str, logger: logging.Logger):
    # read 要抓取 poi 的區域
    with open(target_area) as f:
        coordinates = json.load(f)['features']


    options = Options()
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--lang=en-US")
    options.add_experimental_option("prefs", {"intl.accept_languages": "en"})
    options.binary_location = '/usr/bin/google-chrome'

    a2 = time.time()
    place_set = set()
    # 
    file_path = f"{save_path}/{category}.json"
    
    data = {'check_point': -1}
    if os.path.exists(file_path):
        with open(file_path) as f:
            data = json.load(f)
    # 
    if data['check_point'] == -2:
        logger.debug(f"Category: {category} Skipped")
        return
    # 
    if data['check_point'] >= 0:
        place_set.add((
            info['name'], 
            info['a'], 
            info['keyword'], 
            info['category'], 
            info['lat'], info['lon'], 
            info['address'], 
            info['star'], info['comments']
        ) for info in data[category])
        # for info in data[category]:
        #     place_set.add((info['name'], info['a'], info['keyword'], info['category'], info['lat'], info['lon'], info['address'], info['star'], info['comments']))
        logger.debug(f">> {category} Started from point {data['check_point']+1}")
    else:
        logger.debug(f">> {category} Started from point 0")

    error_point = []
    for idx, point in enumerate(coordinates):
        try:
            if idx <= data['check_point']:
                continue
            
            lat, lon = point['geometry']['coordinates'][1], point['geometry']['coordinates'][0]
            # service = Service()
            driver = webdriver.Chrome(options=options)
            # wait = WebDriverWait(driver, timeout=3)

            driver.get(
                f"https://www.google.com/maps/search/{category}/@{lat},{lon},16z/data=!3m1!4b1!4m6!2m5!3m4!2s{lat},+{lon}!4m2!1d{lon}!2d{lat}?hl=en?entry=ttu"
            )

            processing_period, start = 0, time.time()
            prev_data_length = 0
            while processing_period <= 100:
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
                processing_period = time.time()-start

            content = driver.page_source
            driver.quit()
            soup = Soup(content, "html.parser")
            categories = []
            addresses = []
            comment = []
            # 
            __category = soup.find_all(class_="W4Efsd")
            for outer_div in __category:
                inner_div = outer_div.find('div', class_='W4Efsd')
                if inner_div is not None:
                    span_text = inner_div.find_all('span')
                    categories.append(span_text[0].text)
                    addresses.append(span_text[-1].text if span_text[-1].text!=span_text[0].text else "")
            # 
            __review = soup.find_all(class_="e4rVHe fontBodyMedium")
            if __review != []:
                for outer_span in __review:
                    inner_div = outer_span.find('span', class_='ZkP5Je')
                    if inner_div is not None:
                        star = outer_span.find('span', class_='MW4etd')
                        reviews = outer_span.find('span', class_='UY7F9')
                        comment.append([float(star.text), int(reviews.text[1:-1].replace(",", ""))])
                    else:
                        comment.append(["", ""])
            else:
                comment = [["", ""]] * len(categories)
            # 
            __divs = soup.find_all(class_="qBF1Pd fontHeadlineSmall")
            __arefs = soup.find_all(class_="hfpxzc")
            for i, r in enumerate(zip(__divs, __arefs)):
                href = str(r[1].get('href'))
                lat2, lon2 = find_lat_lon(href)
                if lat2 is not None:
                    if within_distance(lat1=lat, lon1=lon, lat2=lat2, lon2=lon2, max_distance=600):
                        place_set.add((r[0].text, href, category, categories[i], lat2, lon2, addresses[i], comment[i][0], comment[i][1]))
            # 
            if idx % 5 == 0:
                place_name = []
                for info in place_set:
                    place_name.append({"name": info[0], "a": info[1], "keyword": info[2], 'category': info[3], "lat": info[4], "lon": info[5], "address": info[6], "star": info[7], "comments": info[8]})
                
                data[category] = place_name
                data["check_point"] = idx
                data["error"] = error_point
                data["length"] = len(place_name)

                with open(file_path, "w") as f:
                    json.dump(data, f)
            
            if idx % 100 == 0 and idx != 0:
                logger.info(f">> {category} - {idx}/{len(coordinates)} | Time: {round(time.time() - a2, 2)}")
        
        except Exception as e:
            logger.debug(f"Error Messages: {e}")
            error_point.append(idx)

    place_name = []
    for info in place_set:
        # logger.debug(info)
        place_name.append({"name": info[0], "a": info[1], "keyword": info[2], 'category': info[3], "lat": info[4], "lon": info[5], "address": info[6], "star": info[7], "comments": info[8]})

    data[category] = place_name
    data["check_point"] = -2
    data["error"] = error_point
    data["length"] = len(place_name)

    with open(file_path, "w") as f:
        json.dump(data, f)

    logger.debug(f"category: {category} finished | Processing: {round(time.time() - a2, 2)} | Total: {round(time.time() - a1, 2)}")

if __name__ == "__main__":
    from multiprocessing import Pool
    categories = ["bakery", "bank",]
    logger = logging.getLogger("google_crawler_logger")

    
    num_cores = 3
    # logger.debug(f"{'-'*15} CPU Count: {num_cores} {'-'*15}")
    with Pool(num_cores) as pool:
        for category in categories:
            pool.apply_async(
                scrape_data,
                (category, "output", "./test_data.geojson", logger)
            )
        pool.close()
        pool.join()
    

