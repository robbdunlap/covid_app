import pandas as pd
import requests
import pprint   #pretty print
import json
import pathlib

# r = requests.get('https://healthdata.gov/api/action/datastore/search.json?resource_id=fe3c12ae-bdba-49eb-a9fa-5ab44a95b0ae')
# data_out = r.json()
# with open('data/data_out.json', 'w') as f:
#     json.dump(data_out, f)

with open('data/data_out.json') as f:
    r = json.load(f)
print(type(r))

r_json = json.dump(r, fp)
print(type(r_json))

print(r)
#pprint.pprint(r.json())
