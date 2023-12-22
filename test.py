import json

with open("parking_name_ls.json", "r") as f:
    data = json.load(f)['name']

n = list(set([i['res'] for i in data]))
print(len(n))