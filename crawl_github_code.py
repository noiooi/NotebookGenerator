import math
import os
import shutil
import time

import requests
from requests.auth import HTTPBasicAuth
import json
import datetime

# Github URL
URL = 'https://api.github.com/search/'
FIND_CODE_PATH = 'code'
ID = 'kyoungjunpark'
TOKEN = 'xx'
Q_PAYLOAD = 'pandas+read_csv+in:file+extension:ipynb'

payload = {'q': Q_PAYLOAD, 'sort': 'stars',
           'order': 'asc', 'per_page': 100, 'page': 1}

headers = {'Accept': 'application/vnd.github.v3+json'}

repo_list = {}
i = 1
index = 0


with open('res/id') as f_id, open('res/full_name') as f_name:
    repo_id = f_id.read().splitlines()
    name = f_name.read().splitlines()
    for x, y in zip(repo_id, name):
        repo_list[int(x)] = y

# Remove organizations that doesn't contain ipynb file
ipynb_list = []
repo_count = 0
total_iter = 0
for key in repo_list:
    if total_iter % 10000 == 0:
        print(str(ipynb_list))
        if os.path.exists('res/ipynb_list'):
            shutil.rmtree('res/ipynb_list')

        with open('res/ipynb_list', 'w') as f:
            f.write(json.dumps(ipynb_list))

    if repo_count != 140:
        total_iter += 1
        repo_count += 1
        payload['q'] += '+repo:' + str(repo_list[key])
        continue

    payload_str = "&".join("%s=%s" % (k, v) for k, v in payload.items())
    print("batch count: " + str(total_iter))
    r = requests.get(url=URL + FIND_CODE_PATH, auth=HTTPBasicAuth(ID, TOKEN), headers=headers, params=payload_str)
    while r.status_code != 200:
        if r.status_code == 414:
            print("Too long url")
        print("wait 60 sec for API rate limit")
        time.sleep(60)
        r = requests.get(url=URL + FIND_CODE_PATH, auth=HTTPBasicAuth(ID, TOKEN), headers=headers, params=payload_str)

    json_data = r.json()
    total_count = json_data['total_count']
    print("item count: " + str(total_count))

    if total_count == 0:
        payload['q'] = Q_PAYLOAD
        payload_str = "&".join("%s=%s" % (k, v) for k, v in payload.items())
        repo_count = 0
        continue

    if total_count > 1000:
        print("Too much data :<")

    for elem in json_data['items']:
        json_elem = {'repo': elem['repository']['full_name'],
                        'desc': elem['repository']['description'], 'name': elem['name'], 'path': elem['path']}
        ipynb_list.append(json_elem)
        f = open('res/ipynb_list', 'a')

    while math.ceil(total_count / 100.0) != i and i != 10:
        r = requests.get(url=URL + FIND_CODE_PATH, auth=HTTPBasicAuth(ID, TOKEN), headers=headers, params=payload_str)
        while r.status_code != 200:
            print("wait 60 sec for API rate limit")
            time.sleep(60)
            r = requests.get(url=URL + FIND_CODE_PATH, auth=HTTPBasicAuth(ID, TOKEN), headers=headers,
                             params=payload_str)

        for elem in json_data['items']:
            json_elem = {'repo': elem['repository']['full_name'],
                        'desc': elem['repository']['description'], 'name': elem['name'], 'path': elem['path']}
            ipynb_list.append(json_elem)
        payload['page'] = i
        i += 1
        payload_str = "&".join("%s=%s" % (k, v) for k, v in payload.items())
        print("page change: " + str(i))

    payload['page'] = 1
    payload['q'] = Q_PAYLOAD
    i = 1

    print("page change: " + str(i))
    print("current ipynb list size: " + str(len(ipynb_list)))
    repo_count = 0

with open('res/ipynb_list', 'a') as f:
    f.write(json.dumps(ipynb_list))

print(str(ipynb_list))

index = len(repo_list)