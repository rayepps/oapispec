import json
import os

import dictdiffer


def load_asset(name):
    path = os.path.join(os.path.dirname(__file__), f'assets/{name}')
    with open(path) as f:
        return json.load(f)

def load_expected_full_schema_result():
    return load_asset('expected_full_schema_result.json')

def _ensure_dir_exists(path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def write_result(file_name, content, ext='json'):

    path = os.path.join(os.path.dirname(__file__), f'results/{file_name}.{ext}')

    _ensure_dir_exists(path)

    with open(path, 'w+') as file:
        file.write(content)

def diff(result, expected):
    print('### -------- DIFF --------- ###')
    for diff in list(dictdiffer.diff(result, expected)):
        print(diff)
    print('### -------- END DIFF --------- ###')
