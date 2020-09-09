import json
import os
import shutil
import sys
import trace
import time

import requests
import subprocess

import simplejson

from utils.load_data import load_csv
from utils.refine_data import refine_python_code, is_analyzable, remove_related_files, remove_repo

URL = 'https://raw.githubusercontent.com/'
DEFAULT_BRANCH = 'master/'
REPO_PATH = 'res/repo/'

DEFAULT_PATH = os.getcwd()

# virtualenv
PYTHON_BIN = "/home/kyoungjun/NotebookGenerator/venv/bin/python3.6"
PYTHON_LIB = "/home/kyoungjun/vmaf/python/src:/usr/lib/python36.zip:/usr/lib/python3.6:/usr/lib/python3.6/lib-dynload:/home/kyoungjun/NotebookGenerator/venv/lib/python3.6/site-packages:/home/kyoungjun/.local/lib/python3.6/site-packages:/usr/local/lib/python3.6/dist-packages:/usr/local/lib/python3.6/dist-packages/setuptools-40.8.0-py3.6.egg:/usr/lib/python3/dist-packages"


# Load ipynb list
repo_list = []
with open('res/ipynb_list') as f:
    # file_data = f.read()
    data = json.load(f)
    for elem in data:
        tmp_json = {'name': elem['name'], 'repo': elem['repo'], 'path': elem['path']}
        repo_list.append(tmp_json)


# Download ipynb file and Check the data source
# Filter input format only "csv"
# Pandas usage and csv is already checked when crawling through keywords in files
i = 0
for repo_path in repo_list:
    i += 1
    print("Start repo: %s(%d/%d)" % (repo_path, i, len(repo_list)))

    os.chdir(DEFAULT_PATH)
    if not os.path.exists(REPO_PATH + repo_path['repo']):
        os.makedirs(REPO_PATH + repo_path['repo'])
        os.makedirs(REPO_PATH + repo_path['repo'] + '/cover')
    else:
        continue

    r = requests.get(URL + repo_path['repo'] + '/' + DEFAULT_BRANCH + repo_path['path'], allow_redirects=True)
    if r.status_code == 200:
        os.chdir(REPO_PATH + repo_path['repo'])

        refined_name = repo_path['name'].replace(" ", "")
        refined_name = refined_name.replace("*", "")
        refined_name = refined_name.replace("(", "")
        refined_name = refined_name.replace(")", "")
        refined_name = refined_name.replace(">", "")
        refined_name = refined_name.replace("<", "")
        refined_name = refined_name.replace(",", "")

        file_name, file_format = os.path.splitext(refined_name)
        try:
            file_contents = r.json()

            open(refined_name, 'wb').write(r.content)
            subprocess.check_output(['jupyter', 'nbconvert', '--to', 'python', refined_name], stderr=subprocess.PIPE)
            subprocess.check_output(['2to3', '-w', '--no-diffs', file_name + '.py'], stderr=subprocess.PIPE)
        except (json.decoder.JSONDecodeError, simplejson.errors.JSONDecodeError) as e:
            print("Incorrect ipynb(json) format")
            print(e)
            continue
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode()
            print(error_msg)
            continue

        if not is_analyzable(file_name + '.py'):
            print("Unassociated codes are exist")
            continue

        refine_python_code(file_name + '.py')
        load_csv(file_name + '.py', repo_path)
        # tracer = trace.Trace(ignoredirs=[sys.prefix, sys.exec_prefix], trace=1, count=1)

        prev_pkg_name = None
        is_useless_repo = True
        while True:
            print("Start notebook: %s" % REPO_PATH + repo_path['repo'] + '/' + file_name + '.py')
            try:
                # Trace the python file
                ignore_dir = ":".join(sys.path[1:])

                subprocess.check_output([PYTHON_BIN, '-m', 'trace',
                                         "--ignore-dir=" + ignore_dir,
                                         '--count', '-C',
                                         "cover/",
                                         file_name + '.py'], stderr=subprocess.PIPE)

                f = open(file_name + '_trace', "w")
                subprocess.call([PYTHON_BIN, '-m', 'trace',
                                 "--ignore-dir=" + ignore_dir,
                                 '-t', file_name + '.py'], stdout=f)
                print("------------Completed------------")
                is_useless_repo = False
                break
            except subprocess.CalledProcessError as e:
                error_msg = e.stderr.decode()
                if "No module named" in error_msg:
                    print(error_msg)
                    # External library problem
                    pkg_name = (error_msg.split("No module named ", 1)[1])
                    pkg_name = pkg_name.strip()
                    pkg_name = pkg_name.replace("'", "")
                    pkg_name = pkg_name.replace('\\', "")
                    pkg_name = pkg_name.replace('"', "")

                    pkg_name = pkg_name.split(".")[0]
                    try:

                        if prev_pkg_name == pkg_name:
                            raise subprocess.CalledProcessError(returncode=-1, cmd=pkg_name)
                        else:
                            prev_pkg_name = pkg_name
                        subprocess.check_output(['pip', 'install', '--user', pkg_name], stderr=subprocess.PIPE)
                    except subprocess.CalledProcessError as e:
                        print("Cannot handle the Error in the package import")
                        # print(error_msg)
                        # shutil.rmtree(REPO_PATH + repo_path['repo'].split('/')[0])
                        remove_related_files(file_name)
                        break
                elif "No such file or directory" in error_msg:
                    print("CSV data is not loaded")
                    print(error_msg)
                    try:
                        file_path = error_msg.split("No such file or directory: ", 1)[1]
                    except IndexError as e:
                        break
                    if not load_csv(file_path, repo_path):
                        print("Cannot find file: " + file_path)
                        remove_related_files(file_name)
                        break
                elif "does not exist: " in error_msg:
                    try:
                        file_path = error_msg.split("No such file or directory: ", 1)[1]
                    except IndexError as e:
                        break
                    if isinstance(file_path, bytes):
                        file_path = file_path.decode("utf-8")
                    if not load_csv(file_path, repo_path):
                        print("Cannot find file: " + file_path)
                        remove_related_files(file_name)
                        break
                else:
                    print("Error in the code")
                    print(error_msg)
                    # shutil.rmtree(REPO_PATH + repo_path['repo'].split('/')[0])
                    remove_related_files(file_name)
                    break

        # if is_useless_repo:
            # remove_repo(DEFAULT_PATH, REPO_PATH + repo_path['repo'])

    elif r.status_code == 403:
        print("wait 60 sec for API rate limit")
        time.sleep(60)
        print(r.content)
    else:
        print("Server failed")
