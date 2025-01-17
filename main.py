import json
from multiprocessing import Pool, cpu_count, Lock
import logging
import os
# 
import yaml
from dotenv import load_dotenv
load_dotenv()
# 
import stage1
import stage2
import stage3
import stage4
import stage5


# SET global vairables
# global GENRES
global CATEGORIES
global SETTING_CONFIG
global BASE_SAVE_PATH
global NUMBER_THREADS

# SET logging infomation
logger = logging.getLogger("google_crawler_logger")
# stream_handler = logging.StreamHandler()
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s %(levelname)s:%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def __stage_message(msg: str):
    logger.info("============================ ---------------- ============================")
    logger.info(f"============================ {msg} ============================")
    logger.info("============================ ---------------- ============================")

# ===================================================================
# ===================================================================
# ===================================================================
# ===================================================================

NUMBER_THREADS = int(cpu_count() / 2)
NUMBER_THREADS = 1 
# load setting config
with open("./setting.yaml", 'r') as file:
    SETTING_CONFIG = yaml.load(file, Loader=yaml.SafeLoader)
BASE_SAVE_PATH = SETTING_CONFIG["BASE_SAVE_PATH"]

# load POI CATEGORIES
with open("./data/categories.json", 'r') as file:
    CATEGORIES = json.load(file)["categories"]

# load 要搜尋範圍的 geometry
# with open(f'./data/{SETTING_CONFIG["COORDINATES_FILE_NAME"]}.geojson') as f:
#     coordinates = json.load(f)['features']


logger.info(f"""
            ============== init ==============
            資料的存放位置：{BASE_SAVE_PATH}
            整理後的資料存放位置：{BASE_SAVE_PATH}_clean
            啟用的 thread 數量：{NUMBER_THREADS}
            ==================================
            """)

# stage 1: Fetch POI from google map
__stage_message("Starting Stage 1")
logger.info(f"All Categories: {CATEGORIES}")
with Pool(processes=NUMBER_THREADS) as pool:
    for CATEGORY in CATEGORIES:
        # 多個 thread 同時抓一個種類
        pool.apply_async(
            stage1.scrape_data,
            args=(CATEGORY, BASE_SAVE_PATH ,SETTING_CONFIG["TARGET_AREA_FILE_PATH"], logger)
        )
    pool.close()
    pool.join()
__stage_message("Finished Stage 1")

# stage 2: redefine 
__stage_message("Starting Stage 2")

stage2_res = stage2.redefine_category(CATEGORIES, BASE_SAVE_PATH, logger)
if not os.path.exists(f'{BASE_SAVE_PATH}_clean/'):
    os.makedirs(f'{BASE_SAVE_PATH}_clean')

__stage_message("Finished Stage 2")

# check stage2 output
if stage2_res == {}:
    logger.error("Stage2 does not output correct result.")
    raise Exception("Stage2 does not output correct result.")


# stage 3: processing 
__stage_message("Starting Stage 3")
stage3_res = stage3.processing(CATEGORIES, BASE_SAVE_PATH, stage2_res, logger)
__stage_message("Finished Stage 3")

# stage 4: remove
__stage_message("Starting Stage 4")
stage4.remove_repeat(stage3_res, BASE_SAVE_PATH, logger)
__stage_message("Finished Stage 4")

# stage 5: stroe data into database
__stage_message("Starting Stage 5")
__db_connect = f"postgresql://{SETTING_CONFIG["DB_USER"]}:{os.environ["DB_PASSWORD"]}@{SETTING_CONFIG["DB_HOST"]}:{SETTING_CONFIG["DB_PORT"]}/{SETTING_CONFIG["DB_SCHEMAS"]}/{SETTING_CONFIG["DB_TABLE"]}"
logger.info(f"Connect infomation: {__db_connect}")
# stage5.store_data_into_db()

__stage_message("Finished Stage 5")
    

