import math
import time

import requests
from requests.auth import HTTPBasicAuth
import json
import datetime
from urllib.parse import urlencode

# Github URL
URL = 'https://api.github.com/search/'
FIND_REPO_PATH = 'repositories'
FIND_CODE_PATH = 'code'
ID = 'kyoungjunpark'
TOKEN = 'xx'
Q_PAYLOAD = 'language:python+language:js+created:'
KEYWORDS = ['notebook+', 'jupyter+', 'data', 'analysis+']
keyword_index = 0

headers = {'Accept': 'application/vnd.github.v3+json'}
date = datetime.date(2019, 1, 13)
end_date = datetime.date(2020, 7, 1)
time_delta = 30
delta = datetime.timedelta(days=time_delta)

payload = {'q': KEYWORDS[keyword_index] + Q_PAYLOAD + str(date) + '..' + str(date + delta), 'sort': 'stars',
           'order': 'asc', 'per_page': 100, 'page': 1}
payload_str = "&".join("%s=%s" % (k, v) for k, v in payload.items())

results = {}
i = 1
index = 0

with open('id') as f_id, open('full_name') as f_name:
    repo_id = f_id.read().splitlines()
    name = f_name.read().splitlines()
    for x, y in zip(repo_id, name):
        results[int(x)] = y
index = len(results)

while date <= end_date:
    r = requests.get(url=URL + FIND_REPO_PATH, auth=HTTPBasicAuth(ID, TOKEN), headers=headers, params=payload_str)
    # r = requests.get(url=URL + FIND_REPO_PATH, headers=headers, params=payload_str)
    while r.status_code != 200:
        print("wait 60 sec for API rate limit")
        time.sleep(60)
        r = requests.get(url=URL + FIND_REPO_PATH, auth=HTTPBasicAuth(ID, TOKEN), headers=headers, params=payload_str)

    json_data = r.json()
    total_count = json_data['total_count']

    print("total count: " + str(total_count))

    while total_count >= 1000:
        print("Too much data: " + str(total_count))
        if time_delta <= 1:
            time_delta = 1
            delta = datetime.timedelta(days=time_delta)
            print("just do... :<")
            break
        time_delta = math.ceil(time_delta / 2)
        print("time delta: " + str(time_delta))
        delta = datetime.timedelta(days=time_delta)
        print(str(date) + '~' + str(date + delta))
        payload['q'] = Q_PAYLOAD + str(date) + '..' + str(date + delta)
        payload['page'] = 1
        payload_str = "&".join("%s=%s" % (k, v) for k, v in payload.items())
        r = requests.get(url=URL + FIND_REPO_PATH, auth=HTTPBasicAuth(ID, TOKEN), headers=headers, params=payload_str)
        json_data = r.json()
        total_count = json_data['total_count']

    for elem in json_data['items']:
        if elem['id'] not in results:
            f = open('id', 'a')
            f2 = open('full_name', 'a')
            f.write(str(elem['id']) + '\n')
            f2.write(str(elem['full_name']) + '\n')
            results[elem['id']] = elem['full_name']
            index += 1
            f.close()
            f2.close()

    if total_count == 0 or math.ceil(total_count / 100.0) == i or i == 10:
        if keyword_index + 1 == len(KEYWORDS):
            keyword_index = 0
            date += delta
            print(date)
        else:
            keyword_index += 1
        print("keyword change: " + KEYWORDS[keyword_index])
        time_delta = 30
        delta = datetime.timedelta(days=time_delta)
        payload['q'] = KEYWORDS[keyword_index] + Q_PAYLOAD + str(date) + '..' + str(date + delta)
        print(str(date) + '~' + str(date + delta))
        payload['page'] = 1
        i = 1
    else:
        i += 1
        payload['page'] = i
    payload_str = "&".join("%s=%s" % (k, v) for k, v in payload.items())
    print("page change: " + str(i))
    print("stacked_repo: " + str(index))

# print(len(json_data['items']))
print(r.json())
