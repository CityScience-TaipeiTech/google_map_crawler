import json
import time
import os
# from multiprocessing import Pool, cpu_count
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium import webdriver
from bs4 import BeautifulSoup as Soup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# 
# from 
# 
from tool import find_lat_lon, within_distance
# 
import logging
FORMAT = '%(asctime)s %(levelname)s:%(message)s'
logging.basicConfig(level=logging.ERROR, format=FORMAT)
logger = logging.getLogger("google_crawler_logger")
logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)

with open('./test_data.geojson') as f:
    coordinates = json.load(f)['features']


prev_t = time.time()
# init goolge browser
options = Options()
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--lang=en-US")
options.add_experimental_option("prefs", {"intl.accept_languages": "en"})
options.binary_location = '/usr/bin/google-chrome'

def scrape_data(CATEGORY, file_path):
    curr_t = time.time()
    place_set = set()
    # 
    data = {'check_point': -1}
    # TODO: remember 改回來
    if os.path.exists(file_path):
        pass
        # with open(file_path) as f:
        #     data = json.load(f)

    # 表示這個 category 已經完成了
    if data['check_point'] == -2:
        logger.warning(f" Category: [{CATEGORY}] Skipped")
        return
    # 
    elif data['check_point'] >= 0:
        # for info in data[CATEGORY]:
        place_set.add((
                        info['name'], 
                        info['a'], 
                        info['keyword'], 
                        info['category'], 
                        info['lat'], info['lon'], 
                        info['address'], 
                        info['star'], info['comments']
                    ) for info in data[CATEGORY])
        
        logger.info(f" Category: [{CATEGORY}] Started from index {data['check_point']+1}")
    
    else:
        # 所以這是 check_point < 0 && check_point != -2 ??
        logger.info(f" Category: [{CATEGORY}] Started from index 0")
    # 
    error_point = []
    # TODO: 可用 asynic 改善?
    for idx, point in enumerate(coordinates):
        try:
            if idx <= data['check_point']:
                continue

            driver = webdriver.Chrome(options=options)
            wait = WebDriverWait(driver, timeout=3)

            lat, lon = point['geometry']['coordinates'][1], point['geometry']['coordinates'][0]
            
            driver.get(
                f"https://www.google.com/maps/search/{CATEGORY}/@{lat},{lon},16z/data=!3m1!4b1!4m6!2m5!3m4!2s{lat},+{lon}!4m2!1d{lon}!2d{lat}?hl=en?entry=ttu"
            )

            # TODO: why 是 "processing <= 100" ?? 
            # while processing <= 100:
            
            processing_period, startTime = 0, time.time() 
            prev_data_length = 0
            while processing_period <= 100:
                page_html = driver.page_source
                soup = Soup(page_html, "html.parser")
                target_element = soup.find_all(class_="TFQHme")
                # 
                data_length = len(target_element)
                # 
                try:
                    if data_length != prev_data_length:
                        element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.lXJj5c.Hk4XGb')))
                        # element = driver.find_element(By.CSS_SELECTOR, '.lXJj5c.Hk4XGb')
                        prev_data_length = data_length
                    else:
                        '''
                        修復: Message: no such element: Unable to locate element: {"method":"css selector","selector":".HlvSq"} 
                        '''
                        element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.HlvSq')))
                        # element = driver.find_element(By.CSS_SELECTOR, '.HlvSq')
                    # 
                    driver.execute_script("arguments[0].scrollIntoView();", element)
                # 
                except WebDriverException as e:
                    logger.error("\r\n========== WebDriverException ==========")
                    # logger.error(e)
                except NoSuchElementException as e:
                    logger.error("\r\n--------- NoSuchElementException ---------")
                    logger.error(e)
                except Exception as e:
                    logger.error("\r\n--------- Exception ---------")
                    logger.error(e)
                processing_period = time.time() - startTime

            # ========================================================
            # ========================================================
            page_html = driver.page_source
            driver.quit()
            soup = Soup(page_html, "html.parser")
            # 
            categories = []
            addresses = []
            comment = []
            # 抓取 category 以及 address
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
                if lat2 is not None and lat2 is not None:
                    if within_distance(lat1=lat, lon1=lon, lat2=lat2, lon2=lon2, max_distance=600):
                        place_set.add((r[0].text, href, CATEGORY, categories[i], lat2, lon2, addresses[i], comment[i][0], comment[i][1]))
            
            # 每處理 5 個 POI 就先儲存一次
            if idx % 5 == 0:
                place_name = [{"name": info[0], 
                               "a": info[1], 
                               "keyword": info[2], 
                               'category': info[3], 
                               "lat": info[4], "lon": info[5], "address": info[6], 
                               "star": info[7], "comments": info[8]} for info in place_set]
                
                data[CATEGORY] = place_name
                data["check_point"] = idx
                data["error"] = error_point
                data["length"] = len(place_name)
                logger.info(f"[{CATEGORY}] - storing data...")
                with open(file_path, "w") as f:
                    json.dump(data, f)
            
            # 每處理 100 個 POI 輸出一次執行時間
            if idx % 100 == 0 and idx != 0:
                logger.info(f">> {CATEGORY} - {idx}/{len(coordinates)} | Time: {round(time.time() - prev_t, 2)}")
        # 
        except Exception as e:
            logger.error(e)
            error_point.append(idx)
    
    # 處理 for loop 最後一個批次的資料
    place_name = [{"name": info[0], 
                    "a": info[1], 
                    "keyword": info[2], 
                    'category': info[3], 
                    "lat": info[4], "lon": info[5], "address": info[6], 
                    "star": info[7], "comments": info[8]} for info in place_set]
    data[CATEGORY] = place_name
    data["check_point"] = -2
    data["error"] = error_point
    data["length"] = len(place_name)
    with open(file_path, "w") as f:
        json.dump(data, f)

    logger.info(f"CATEGORY: {CATEGORY} finished | Processing: {round(time.time() - curr_t, 2)} | Total: {round(time.time() - prev_t, 2)}")


if __name__ == "__main__":
    # 測試功能
    import cProfile
    from multiprocessing import Pool, cpu_count, Lock

    with Pool(processes=10) as pool:
        pool.apply_async(
            scrape_data,
            args=("store", "./data/dwq.json")
        )
        pool.close()
        pool.join()

    # cProfile.run('scrape_data("moving+company", "./data/accounting.json")')
    scrape_data("store", "./data/dwq.json")