import json
import logging


# def __read_json_files(folder_path, logger: logging.Logger) -> list:

#     if not os.path.exists(folder_path):
#         logger.warning(f"Not found: {folder_path}")
#         return []

#     json_files = []
#     files = os.listdir(folder_path)
#     for file_name in files:
#         if file_name.endswith(".json"):
#             json_files.append(file_name.split('.json')[0])

#     return json_files

def __remove_repeat(category: list, buildings_list: list, logger: logging.Logger):
    tuple_list = [tuple((k, v) for k, v in d.items() if k != 'keyword') for d in buildings_list]
    tmp = [[v for k, v in d.items() if k == 'keyword'][0] for d in buildings_list]
    # 
    unique_tuples = set(tuple_list)
    unique_list = [dict(t) for t in unique_tuples]
    # 
    for i, d in enumerate(unique_list):
        d['keyword'] = tmp[i]
        unique_list[i] = d
    # 
    logger.info(f'{category}: {len(buildings_list)}/{len(unique_list)}')
    
    return unique_list, len(buildings_list) > len(unique_list)


def remove_repeat(categories: list, file_path: str, logger: logging.Logger):
    for category in categories:
        save_file_path = f'{file_path}_clean/{category}.json'
        
        with open(save_file_path, 'r') as file:
            data = json.load(file)

        data['buildings'], cond = __remove_repeat(category, data['buildings'], logger)
        data['length'] = len(data['buildings'])
        if cond:
            with open(save_file_path, 'w') as file:
                json.dump(data, file, indent=2)


