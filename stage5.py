import os
import regex
import json
import pandas as pd
from deep_translator import GoogleTranslator
from sqlalchemy import create_engine
import logging

# Function to check if a character is a mathematical alphanumeric symbol
def __is_math_alphanum(char):
    # Unicode range for Mathematical Alphanumeric Symbols: U+1D400–U+1D7FF
    return 0x1D400 <= ord(char) <= 0x1D7FF


def store_data_into_db(url:str, logger:logging.Logger):
    engine = create_engine(url)
    # 
    buildings_list = []
    for f in os.listdir('./boston_clean2/'):
        data = json.load(open(f'./boston_clean2/{f}'))
        buildings = data['buildings']
        try:
            # category_en = translator.translate(f.split('.json')[0], dest='en').text
            category_en = GoogleTranslator(source='auto', target='en').translate(f.split('.json')[0])
            print(category_en, f.split('.json')[0])
            for building in buildings:
                building['name'] = ''.join(char for char in building['name'] if not __is_math_alphanum(char))
                building['address'] = ''.join(char for char in building['address'] if not __is_math_alphanum(char))
                building['name'] = regex.sub(r'[^\p{L}\p{N}\p{P}\p{Z}]+', '', building['name'])
                building['address'] = regex.sub(r'[^\p{L}\p{N}\p{P}\p{Z}]+', '', building['address'])
                building['category_en'] = category_en
                # 
                if type(building['star']) != float: 
                    building['star'] = -1
                if building['comments'] == '': 
                    building['comments'] = 0
                # 
                buildings_list.append(
                    [
                        building['name'], 
                        building['category'], 
                        building['lat'], building['lon'], building['address'], 
                        building['star'], building['comments'], 
                        building['keyword'], building['category_en']
                    ])
        except:
            logger.error(f.split('.json')[0])

    columns = ['name', 'category', 'lat', 'lng', 'address', 'star', 'comments', 'keyword', 'category_en']
    df = pd.DataFrame(buildings_list, columns=columns)

    try:
        df.to_sql('poi_buildings', engine, if_exists='append', index=False)
        logger.info("Data inserted successfully!")

    except Exception as e:
        logger.error(f"Error while inserting data:\r\n {e}")
    