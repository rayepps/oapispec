import json

import pytest

from oapispec.core import utils
from oapispec.core.utils import immutable


def test_merge_simple_dicts_without_precedence():
    a = {'a': 'value'}
    b = {'b': 'other value'}
    assert utils.merge(a, b) == {'a': 'value', 'b': 'other value'}

def test_merge_simple_dicts_with_precedence():
    a = {'a': 'value', 'ab': 'overwritten'}
    b = {'b': 'other value', 'ab': 'keep'}
    assert utils.merge(a, b) == {'a': 'value', 'b': 'other value', 'ab': 'keep'}

def test_merge_recursions():
    a = {
        'a': 'value',
        'ab': 'overwritten',
        'nested_a': {
            'a': 'nested'
        },
        'nested_a_b': {
            'a': 'a only',
            'ab': 'overwritten'
        }
    }
    b = {
        'b': 'other value',
        'ab': 'keep',
        'nested_b': {
            'b': 'nested'
        },
        'nested_a_b': {
            'b': 'b only',
            'ab': 'keep'
        }
    }
    assert utils.merge(a, b) == {
        'a': 'value',
        'b': 'other value',
        'ab': 'keep',
        'nested_a': {
            'a': 'nested'
        },
        'nested_b': {
            'b': 'nested'
        },
        'nested_a_b': {
            'a': 'a only',
            'b': 'b only',
            'ab': 'keep'
        }
    }

def test_merge_recursions_with_empty():
    a = {}
    b = {
        'b': 'other value',
        'ab': 'keep',
        'nested_b': {
            'b': 'nested'
        },
        'nested_a_b': {
            'b': 'b only',
            'ab': 'keep'
        }
    }
    assert utils.merge(a, b) == b

def test_no_transform():
    assert utils.camel_to_dash('test') == 'test'

@pytest.mark.parametrize('value,expected', [
    ('aValue', 'a_value'),
    ('aLongValue', 'a_long_value'),
    ('Upper', 'upper'),
    ('UpperCase', 'upper_case'),
])

def test_transform(value, expected):
    assert utils.camel_to_dash(value) == expected

def test_immutable_raises_when_set():
    obj = immutable(x=2, y=23)

    with pytest.raises(TypeError):
        obj['x'] = 5

    with pytest.raises(TypeError):
        obj.x = 5

    with pytest.raises(TypeError):
        del obj['x']

    with pytest.raises(TypeError):
        del obj.x

def test_immutable_none_comparison():
    obj = immutable(x=2, y=23)
    isEqual = obj == None
    assert isEqual is not True

def test_immutable_repr_dumps_json():
    obj = immutable(x=2, y=23)
    r = repr(obj)
    json.loads(r)

def test_immutable_str_dumps_json():
    obj = immutable(x=2, y=23)
    s = str(obj)
    json.loads(s)

def test_immutable_equality():
    a = immutable(x=2, y=23)
    b = immutable(x=2, y=23)

    assert a == b
