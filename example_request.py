import requests
import json
url = 'http://localhost:5000'
route = '/hotel_predictions'
params = {'quantity': '1', 'arrival': '2021-11-30', 'departure': '2021-12-04', 'state': 'CA', 'parent_chain': None}

response = requests.get(url + route, params=params)

if response.status_code == 200:
    obj = response.json()
    print(json.dumps(obj, indent=4))
else:
    print(response.status_code)
