import json
import logging

def redefine_category(categories: list, file_path: str, logger: logging.Logger) -> dict:
    '''
    重新定義所有分類
    '''
    new_categories = []
    for category in categories:
        with open(f"{file_path}/{category}.json", 'r') as file:
            data = json.load(file)

        for place in data[category]:
            category = place['category']
            if category != "" and category not in new_categories:
                new_categories.append(category)
        logger.info(f"Redefine category: {category}  ")

    res=  {category: [] for category in new_categories}
    # print(res)
    return res
    # return {category: [] for category in new_categories}