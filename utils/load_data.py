import os

import requests

URL = 'https://raw.githubusercontent.com/'
DEFAULT_BRANCH = 'master/'
REPO_PATH = 'res/repo/'


def load_csv(file_path, repo_path):
    result = False
    file_path = file_path.strip()
    file_path = file_path.replace("'", "")
    file_path = file_path.replace('"', "")
    file_path = file_path.replace('\n', "")

    file_format = file_path.split(".")[-1]
    if file_format == "py":
        result = load_csv_py(file_path, repo_path)
    elif file_format == "csv" or file_format == "data":
        print("Try to load file: " + file_path)
        result = load_csv_csv(file_path, repo_path)
    else:
        print("Wrong file format: " + file_format)

    return result


def load_csv_py(file_path, repo_path):
    is_loaded = False

    with open(file_path, "r") as f:
        lines = f.readlines()
        for line in lines:
            if "read_csv" in line:
                csv_path = line[line.find("(") + 1:line.find(")")]
                csv_path = csv_path.strip()
                csv_path = csv_path.replace("'", "")
                csv_path = csv_path.replace('"', "")
                csv_path = csv_path.replace('\n', "")

                csv_path.strip()
                initial_path = repo_path['path'].split("/")[:-1]

                if os.path.exists(csv_path):
                    print("Already csv file exist: " + csv_path)
                    continue

                print("Try to load file: " + csv_path)
                while True:
                    if len(initial_path) != 0:
                        print("Request url: " + URL + repo_path['repo'] + '/' + DEFAULT_BRANCH + "/".join(
                            initial_path) + "/" + csv_path)
                        r = requests.get(
                            URL + repo_path['repo'] + '/' + DEFAULT_BRANCH + "/".join(initial_path) + "/" + csv_path,
                            allow_redirects=True)
                    else:
                        print("Request url: " + URL + repo_path['repo'] + '/' + DEFAULT_BRANCH + csv_path)
                        r = requests.get(URL + repo_path['repo'] + '/' + DEFAULT_BRANCH + csv_path,
                                         allow_redirects=True)
                    if r.status_code == 200:
                        print("Save CSV file: " + csv_path)
                        paths = csv_path.split("/")[:-1]
                        if len(paths) != 0 and not os.path.exists("/".join(paths)):
                            os.makedirs("/".join(paths))
                        open(csv_path, 'wb').write(r.content)
                        is_loaded = True
                        break
                    else:
                        if len(initial_path) == 0:
                            print("Cannot find the csv file in any path: " + csv_path)
                            break
                        else:
                            initial_path = initial_path[:-1]
                            print("Change initial path to: " + "/".join(initial_path))

    return is_loaded


def load_csv_csv(file_path, repo_path):
    is_loaded = False
    initial_path = repo_path['path'].split("/")[:-1]
    if os.path.exists(file_path):
        print("Already csv file exist")
        return True

    while True:
        if len(initial_path) != 0:
            print("Request url: " + URL + repo_path['repo'] + '/' + DEFAULT_BRANCH + "/".join(
                initial_path) + "/" + file_path)
            r = requests.get(URL + repo_path['repo'] + '/' + DEFAULT_BRANCH + "/".join(initial_path) + "/" + file_path,
                             allow_redirects=True)
        else:
            print("Request url: " + URL + repo_path['repo'] + '/' + DEFAULT_BRANCH + file_path)
            r = requests.get(URL + repo_path['repo'] + '/' + DEFAULT_BRANCH + file_path,
                             allow_redirects=True)

        if r.status_code == 200:
            print("Save CSV file: " + file_path)
            paths = file_path.split("/")[:-1]
            if len(paths) != 0 and not os.path.exists("/".join(paths)):
                os.makedirs("/".join(paths))
            open(file_path, 'wb').write(r.content)
            is_loaded = True
            break
        else:
            if len(initial_path) == 0:
                print("Cannot find the csv file in any path: " + file_path)
                break
            else:
                initial_path = initial_path[:-1]
                print("Change initial path to: " + "/".join(initial_path))

    return is_loaded