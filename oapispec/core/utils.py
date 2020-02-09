import re

from http import HTTPStatus
from collections import OrderedDict
from copy import deepcopy

from oapispec.core.immutable import Immutable


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


def not_none(data):
    '''
    Remove all keys where value is None

    :param dict data: A dictionary with potentially some values set to None
    :return: The same dictionary without the keys with values to ``None``
    :rtype: dict
    '''
    return dict(OrderedDict((k, v) for k, v in sorted(data.items()) if v is not None))
