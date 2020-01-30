import inspect
import copy
from datetime import datetime, date
from dataclasses import dataclass
from typing import List
from collections import OrderedDict

from tests import utils
from oapispec.core import model_builder


def test_model_as_flat_dict():

    @dataclass
    class Person:
        age: int
        birthdate: date
        last_login: datetime
        name: str = 'bart'

    person = Person(23, 'july', None, name='greg')

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
            }
        },
        'type': 'object'
    }

    utils.diff(result, expected)

    assert result == expected


def test_model_as_nested_dict():

    class Address:
        road: str

    address = model_builder.build_model(Address)

    assert address.__schema__ == {
        'properties': {
            'road': {
                'type': 'string'
            },
        },
        'type': 'object'
    }

    class Person:
        name: str
        age: int
        birthdate: str
        address: Address

    person = model_builder.build_model(Person)

    assert person.__schema__ == {
        # 'required': ['address'],
        'properties': {
            'name': {
                'type': 'string'
            },
            'age': {
                'type': 'integer'
            },
            'birthdate': {
                'type': 'string',
            },
            'address': {
                '$ref': '#/definitions/Address',
            }
        },
        'type': 'object'
    }
