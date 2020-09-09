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
RESOURCE_PATH = 'res/'
ID = 'kyoungjunpark'
TOKEN = 'xx'
Q_PAYLOAD = 'language:python+language:js+language:jupyter+created:'
KEYWORDS = ['python+']
# Done: notebook+, jupyter+, 'data+' 'analysis+'
keyword_index = 0

headers = {'Accept': 'application/vnd.github.v3+json'}
date = datetime.datetime(2015, 7, 15, 12, 23, 38)
end_date = datetime.datetime(2020, 7, 1)
TIME_SPAN = 3600 * 24 * 1
time_delta = TIME_SPAN
delta = datetime.timedelta(seconds=time_delta)


payload = {'q': KEYWORDS[keyword_index] + Q_PAYLOAD + str(date.isoformat()) + '..' + str((date + delta).isoformat()), 'sort': 'stars',
           'order': 'asc', 'per_page': 100, 'page': 1}
payload_str = "&".join("%s=%s" % (k, v) for k, v in payload.items())

print(str(date) + '~' + str(date + delta))

results = {}
i = 1

with open('res/id') as f_id, open('res/full_name') as f_name:
    repo_id = f_id.read().splitlines()
    name = f_name.read().splitlines()
    for x, y in zip(repo_id, name):
        results[int(x)] = y

index = len(results)

while date <= end_date:
    r = requests.get(url=URL + FIND_REPO_PATH, auth=HTTPBasicAuth(ID, TOKEN), headers=headers, params=payload_str)
    # r = requests.get(url=URL + FIND_REPO_PATH, headers=headers, params=payload_str)
    while r.status_code == 403:
        print("wait 60 sec for API rate limit")
        time.sleep(60)
        r = requests.get(url=URL + FIND_REPO_PATH, auth=HTTPBasicAuth(ID, TOKEN), headers=headers, params=payload_str)

    json_data = r.json()
    total_count = json_data['total_count']
    print("total count: " + str(total_count))

    while total_count >= 1000:
        print("Too much data: " + str(total_count))
        if time_delta <= 100:
            time_delta = 100
            delta = datetime.timedelta(seconds=time_delta)
            print("just do... :<")
            break
        time_delta = math.ceil(time_delta / 2)
        print("time delta: " + str(time_delta))
        delta = datetime.timedelta(seconds=time_delta)
        print(str(date) + '~' + str(date + delta))
        payload['q'] = Q_PAYLOAD + str(date.isoformat()) + '..' + str((date + delta).isoformat())
        payload['page'] = 1
        payload_str = "&".join("%s=%s" % (k, v) for k, v in payload.items())
        r = requests.get(url=URL + FIND_REPO_PATH, auth=HTTPBasicAuth(ID, TOKEN), headers=headers, params=payload_str)
        json_data = r.json()
        total_count = json_data['total_count']

    for elem in json_data['items']:
        if elem['id'] not in results:
            f = open(RESOURCE_PATH + 'id', 'a')
            f2 = open(RESOURCE_PATH + 'full_name', 'a')
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
        time_delta = TIME_SPAN
        delta = datetime.timedelta(seconds=time_delta)
        payload['q'] = KEYWORDS[keyword_index] + Q_PAYLOAD + str(date.isoformat()) + '..' + str((date + delta).isoformat())
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
