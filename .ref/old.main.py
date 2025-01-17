import os
import json
import logging
from multiprocessing import Pool, cpu_count
from utils.crawl_data import scrape_data
from utils.remove_repeat_elem import read_json_files, remove_repeat
# from processing import remove_repeat
from utils.postgres import postgres_db


# PARAMS
NUM_CORES = 30
DATA_PATH = 'hisnchu_point_100m_1km_buff.geojson'
DB_URL = "postgresql://airflow:airflow@10.100.2.124:5432/postgres/hsinchu_abm"
SAVE_FOLDER = 'hisnchu'

# settings
logger = logging.getLogger("google_crawler_logger")
logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)
logger.debug(f"{'-'*15} CPU Count: {NUM_CORES} {'-'*15}")

# read files
if not os.path.exists(f'{SAVE_FOLDER}/'):
    os.makedirs(SAVE_FOLDER)
    
with open(DATA_PATH) as f:
    coordinates = json.load(f)['features']

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

# ----------------------------------------------------------------------------------

def main():
    # scape data
    # num_cores = 30
    # logger.debug(f"{'-'*15} CPU Count: {num_cores} {'-'*15}")
    with Pool(NUM_CORES) as pool:
        for ty in genres:
            pool.apply_async(
                scrape_data,
                (ty, coordinates, SAVE_FOLDER, logger)
            )
        pool.close()
        pool.join()

    # redefine type
    new_genres = []
    for ty in genres:
        file_path = f'{SAVE_FOLDER}/{ty}.json'
        with open(file_path, 'r') as file:
            data = json.load(file)

        for place in data[ty]:
            category = place['category']
            if category != "" and category not in new_genres:
                new_genres.append(category)
    
    all_dict = {ty: [] for ty in new_genres}

    # processing
    for ty in genres:
        file_path = f'{SAVE_FOLDER}/{ty}.json'

        with open(file_path, 'r') as file:
            data = json.load(file)

        for place in data[ty]:
            category = place['category']
            if category != '':
                all_dict[category].append(place)

    count = 0
    for k, v in all_dict.items():
        tmp = {}
        tmp['buildings'] = v
        tmp['length'] = len(v)
        count += len(v)
        k = k.replace('/', '+')

        with open(f'{SAVE_FOLDER}_clean/{k}.json', 'w') as file:
            json.dump(tmp, file, indent=2)

    print(f"Total:", count)
    
    # remove repeat
    json_files_list = read_json_files(SAVE_FOLDER)

    print(len(json_files_list))
    print(json_files_list)

    for ty in json_files_list:
        if not os.path.exists(f'{SAVE_FOLDER}_clean/'):
            os.makedirs(f'{SAVE_FOLDER}_clean')
        
        file_path = f'{SAVE_FOLDER}_clean/{ty}.json'
        with open(file_path, 'r') as file:
            data = json.load(file)

        data['buildings'], cond = remove_repeat(ty, data['buildings'])
        data['length'] = len(data['buildings'])
        if cond:
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=2)
    
    # building process
    postgres_db(DB_URL)


if __name__ == '__main__':
    main()
