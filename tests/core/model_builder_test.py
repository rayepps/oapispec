import inspect
import copy
from datetime import datetime, date
# from dataclasses import dataclass
from typing import List
from collections import OrderedDict

from tests import utils
from oapispec.core import model_builder


def test_model_builder():

    class Address:
        road: str
        unit: str
        state: str

    class Person:
        age: int
        birthdate: date
        last_login: datetime
        name: str = 'bart'
        is_active: bool = False
        metadata: dict = {}
        address: Address
        roles: List[str]

    model = model_builder.build_model(Person)

    result = model.__schema__
    expected = {
        'properties': {
            'name': {
                'type': 'string'
            },
            'age': {
                'type': 'integer'
            },
            'birthdate': {
                'type': 'string',
                'format': 'date'
            },
            'last_login': {
                'type': 'string',
                'format': 'date-time'
            },
            'is_active': {
                'type': 'boolean'
            },
            'metadata': {
                'type': 'object'
            },
            'address': {
                '$ref': '#/definitions/Address',
            },
            'roles': {
                'type': 'array',
                'items': {
                    'type': 'string'
                }
            }
        },
        'type': 'object'
    }

    utils.diff(result, expected)

    assert result == expected
