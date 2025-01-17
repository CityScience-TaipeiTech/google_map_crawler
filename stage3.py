import json
import logging

def processing(categories: list, file_path:str , all_dict:dict, logger: logging.Logger) -> list:
    for category in categories:
        with open(f'{file_path}/{category}.json', 'r') as file:
            data = json.load(file)

        for place in data[category]:
            if (category:=place['category']) != '':
                all_dict[category].append(place)

    count = 0
    new_cateories = []
    for k, v in all_dict.items():
        tmp = {}
        tmp['buildings'] = v
        tmp['length'] = len(v)
        count += len(v)
        k = k.replace('/', '+')
        new_cateories.append(k)
        with open(f'{file_path}_clean/{k}.json', 'w') as file:
            json.dump(tmp, file, indent=2)
        
            logger.info(f"Store processed file: {k}.json")
    
    logger.info(f"Total: {count}")
    return new_cateories