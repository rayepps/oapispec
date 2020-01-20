import json
import os


def load_asset(name):
    path = os.path.join(os.path.dirname(__file__), f'assets/{name}')
    with open(path) as f:
        return json.load(f)

def load_expected_mock_schema_result():
    return load_asset('expected_mock_schema_result.json')
