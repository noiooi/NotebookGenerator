import os
import shutil

REMOVE_KEYWORD = ["plt.show", "get_ipython"]
UNASSOCIATED_KEYWORD = ["PIL"]
MUST_KEYWORD = ["pandas", "read_csv"]
INSERT_KEYWORD = ["%%matplotlib inline"]

# ADDITIONAL_CODE_KEYWORD = ["plt.show()"]

# Notes
# 1. sklearn.cross_validation is deprecated
# 2. DataFrame ix is deprecated
# 3. 'DataFrame' object has no attribute 'sort' is deprecated


def refine_python_code(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()
    with open(file_path, "w") as f:
        for line in lines:
            is_remove = False
            for keyword in REMOVE_KEYWORD:
                if keyword in line:
                    is_remove = True
                    break
            if not is_remove:
                f.write(line)
            else:
                f.write("# " + line)
    return True


def is_analyzable(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()
        for keyword in UNASSOCIATED_KEYWORD:
            if keyword in lines:
                return False
    return True


def remove_related_files(file_name):
    for f in os.listdir():
        if f.startswith(file_name + ".ipynb") or f.startswith(file_name + '.py'):
            os.remove(f)
    for f in os.listdir('cover/'):
        if f.startswith(file_name):
            os.remove(f)
    return True


def remove_repo(default_path, repo_path):
    os.chdir(default_path)
    shutil.rmtree(repo_path)
    if len(os.listdir(repo_path.split("/")[0])) == 0:
        shutil.rmtree(repo_path.split("/")[0])

    return True
