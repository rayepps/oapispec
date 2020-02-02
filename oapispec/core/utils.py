import re

from http import HTTPStatus
from collections import OrderedDict
from copy import deepcopy

from oapispec.core.immutable import Immutable


FIRST_CAP_RE = re.compile('(.)([A-Z][a-z]+)')
ALL_CAP_RE = re.compile('([a-z0-9])([A-Z])')


def immutable(obj=None, **kwargs):
    if obj is not None:
        return Immutable(**obj)
    return Immutable(**kwargs)

def merge(first, second):
    '''
    Recursively merges two dictionaries.

    Second dictionary values will take precedence over those from the first one.
    Nested dictionaries are merged too.

    :param dict first: The first dictionary
    :param dict second: The second dictionary
    :return: the resulting merged dictionary
    :rtype: dict
    '''
    result = deepcopy(first)
    for key, value in second.items():
        if key in result and isinstance(result[key], dict):
            result[key] = merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def camel_to_dash(value):
    '''
    Transform a CamelCase string into a low_dashed one

    :param str value: a CamelCase string to transform
    :return: the low_dashed string
    :rtype: str
    '''
    first_cap = FIRST_CAP_RE.sub(r'\1_\2', value)
    return ALL_CAP_RE.sub(r'\1_\2', first_cap).lower()


def not_none(data):
    '''
    Remove all keys where value is None

    :param dict data: A dictionary with potentially some values set to None
    :return: The same dictionary without the keys with values to ``None``
    :rtype: dict
    '''
    return dict((k, v) for k, v in data.items() if v is not None)


def not_none_sorted(data):
    '''
    Remove all keys where value is None

    :param OrderedDict data: A dictionary with potentially some values set to None
    :return: The same dictionary without the keys with values to ``None``
    :rtype: OrderedDict
    '''
    return dict(OrderedDict((k, v) for k, v in sorted(data.items()) if v is not None))
