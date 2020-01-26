
import re
import pytz
import pytest

from datetime import date, datetime
from six import text_type

from oapispec.core import inputs


def test_date_from_iso8601_schema():
    assert inputs.date_from_iso8601.__schema__ == {'type': 'string', 'format': 'date'}

def test_datetime_from_iso8601_schema():
    assert inputs.datetime_from_iso8601.__schema__ == {'type': 'string', 'format': 'date-time'}

def test_url_schema():
    assert inputs.url.__schema__ == {'type': 'string', 'format': 'url'}

def test_ip_schema():
    assert inputs.ip.__schema__ == {'type': 'string', 'format': 'ip'}

def test_ipv4_schema():
    assert inputs.ipv4.__schema__ == {'type': 'string', 'format': 'ipv4'}

def test_ipv6_schema():
    assert inputs.ipv6.__schema__ == {'type': 'string', 'format': 'ipv6'}

def test_email_schema():
    assert inputs.email.__schema__ == {'type': 'string', 'format': 'email'}

def test_regex_schema():
    assert inputs.regex(r'^[0-9]+$').__schema__ == {'type': 'string', 'pattern': '^[0-9]+$'}

def test_boolean_schema():
    assert inputs.boolean.__schema__ == {'type': 'boolean'}

def test_date_schema():
    assert inputs.date.__schema__ == {'type': 'string', 'format': 'date'}

def test_natural_schema():
    assert inputs.natural.__schema__ == {'type': 'integer', 'minimum': 0}

def test_positive_schema():
    assert inputs.positive.__schema__ == {'type': 'integer', 'minimum': 0, 'exclusiveMinimum': True}

def test_int_range_schema():
    assert inputs.int_range(1, 5).__schema__ == {'type': 'integer', 'minimum': 1, 'maximum': 5}

def test_iso8601interval_schema():
    assert inputs.iso8601interval.__schema__ == {'type': 'string', 'format': 'iso8601-interval'}
