import requests
import json
url = 'http://localhost:5000'
route = '/hotel_predictions'
params = {'quantity': '1', 'arrival': '2021-12-15', 'departure': '2021-12-16', 'state': 'UT', 'parent_chain': 'hilton'}

response = requests.get(url + route, params=params)

if response.status_code == 200:
    obj = response.json()
    print(json.dumps(obj, indent=4))
else:
    print(response.status_code)
