
from collections import OrderedDict
from datetime import date, datetime
from decimal import Decimal
from functools import partial

import pytest

from oapispec import fields


class FieldTestCase:
    field_class = None

class BaseFieldTestMixin:
    def test_description(self):
        field = self.field_class(description='A description')
        assert 'description' in field.__schema__
        assert field.__schema__['description'] == 'A description'

    def test_title(self):
        field = self.field_class(title='A title')
        assert 'title' in field.__schema__
        assert field.__schema__['title'] == 'A title'

    def test_required(self):
        field = self.field_class(required=True)
        assert field.required

    def test_readonly(self):
        field = self.field_class(readonly=True)
        assert 'readOnly' in field.__schema__
        assert field.__schema__['readOnly']


class NumberTestMixin:
    def test_min(self):
        field = self.field_class(minimum=0)
        assert 'minimum' in field.__schema__
        assert field.__schema__['minimum'] == 0
        assert 'exclusiveMinimum' not in field.__schema__

    def test_min_as_callable(self):
        field = self.field_class(minimum=lambda: 0)
        assert 'minimum' in field.__schema__
        assert field.__schema__['minimum'] == 0

    def test_min_exlusive(self):
        field = self.field_class(minimum=0, exclusive_minimum=True)
        assert 'minimum' in field.__schema__
        assert field.__schema__['minimum'] == 0
        assert 'exclusiveMinimum' in field.__schema__
        assert field.__schema__['exclusiveMinimum'] is True

    def test_max(self):
        field = self.field_class(maximum=42)
        assert 'maximum' in field.__schema__
        assert field.__schema__['maximum'] == 42
        assert 'exclusiveMaximum' not in field.__schema__

    def test_max_as_callable(self):
        field = self.field_class(maximum=lambda: 42)
        assert 'maximum' in field.__schema__
        assert field.__schema__['maximum'] == 42

    def test_max_exclusive(self):
        field = self.field_class(maximum=42, exclusive_maximum=True)
        assert 'maximum' in field.__schema__
        assert field.__schema__['maximum'] == 42
        assert 'exclusiveMaximum' in field.__schema__
        assert field.__schema__['exclusiveMaximum'] is True

    def test_mulitple_of(self):
        field = self.field_class(multiple=5)
        assert 'multipleOf' in field.__schema__
        assert field.__schema__['multipleOf'] == 5


class StringTestMixin(object):
    def test_min_length(self):
        field = self.field_class(min_length=1)
        assert 'minLength' in field.__schema__
        assert field.__schema__['minLength'] == 1

    def test_min_length_as_callable(self):
        field = self.field_class(min_length=lambda: 1)
        assert 'minLength' in field.__schema__
        assert field.__schema__['minLength'] == 1

    def test_max_length(self):
        field = self.field_class(max_length=42)
        assert 'maxLength' in field.__schema__
        assert field.__schema__['maxLength'] == 42

    def test_max_length_as_callable(self):
        field = self.field_class(max_length=lambda: 42)
        assert 'maxLength' in field.__schema__
        assert field.__schema__['maxLength'] == 42

    def test_pattern(self):
        field = self.field_class(pattern='[a-z]')
        assert 'pattern' in field.__schema__
        assert field.__schema__['pattern'] == '[a-z]'


class TestRawField(BaseFieldTestMixin, FieldTestCase):
    ''' Test Raw field AND some common behaviors'''

    def field_class(self, **kwargs):
        return fields.raw(**kwargs)

    def test_type(self):
        field = fields.raw()
        assert field.__schema__['type'] == 'object'

    def test_default(self):
        field = fields.raw(default='aaa')
        assert field.__schema__['default'] == 'aaa'

    def test_default_as_callable(self):
        field = fields.raw(default=lambda: 'aaa')
        assert field.__schema__['default'] == 'aaa'


class TestStringField(StringTestMixin, BaseFieldTestMixin, FieldTestCase):

    def field_class(self, **kwargs):
        return fields.string(**kwargs)

    def test_defaults(self):
        field = fields.string()
        assert not field.required
        assert field.__schema__ == {'type': 'string'}

    def test_with_enum(self):
        enum = ['A', 'B', 'C']
        field = fields.string(enum=enum)
        assert not field.required
        assert field.__schema__ == {'type': 'string', 'enum': enum, 'example': enum[0]}

    def test_with_empty_enum(self):
        field = fields.string(enum=[])
        assert not field.required
        assert field.__schema__ == {'type': 'string'}

    def test_with_callable_enum(self):
        enum = lambda: ['A', 'B', 'C']  # noqa
        field = fields.string(enum=enum)
        assert not field.required
        assert field.__schema__ == {'type': 'string', 'enum': ['A', 'B', 'C'], 'example': 'A'}

    def test_with_empty_callable_enum(self):
        enum = lambda: []  # noqa
        field = fields.string(enum=enum)
        assert not field.required
        assert field.__schema__ == {'type': 'string'}

    def test_with_default(self):
        field = fields.string(default='aaa')
        assert field.__schema__ == {'type': 'string', 'default': 'aaa'}



class TestIntegerField(BaseFieldTestMixin, NumberTestMixin, FieldTestCase):

    def field_class(self, **kwargs):
        return fields.integer(**kwargs)

    def test_defaults(self):
        field = fields.integer()
        assert not field.required
        assert field.__schema__ == {'type': 'integer'}

    def test_with_default(self):
        field = fields.integer(default=42)
        assert not field.required
        assert field.__schema__ == {'type': 'integer', 'default': 42}

    def test_decode_error(self):
        field = fields.integer()



class TestBooleanField(BaseFieldTestMixin, FieldTestCase):

    def field_class(self, **kwargs):
        return fields.boolean(**kwargs)

    def test_defaults(self):
        field = fields.boolean()
        assert not field.required
        assert field.__schema__ == {'type': 'boolean'}

    def test_with_default(self):
        field = fields.boolean(default=True)
        assert not field.required
        assert field.__schema__ == {'type': 'boolean', 'default': True}


class TestFloatField(BaseFieldTestMixin, NumberTestMixin, FieldTestCase):

    def field_class(self, **kwargs):
        return fields.float(**kwargs)

    def test_defaults(self):
        field = fields.float()
        assert not field.required
        assert field.__schema__ == {'type': 'number'}

    def test_with_default(self):
        field = fields.float(default=0.5)
        assert not field.required
        assert field.__schema__ == {'type': 'number', 'default': 0.5}


class TestDatetimeField(BaseFieldTestMixin, FieldTestCase):

    def field_class(self, **kwargs):
        return fields.date_time(**kwargs)

    def test_defaults(self):
        field = fields.date_time()
        assert not field.required
        assert field.__schema__ == {'type': 'string', 'format': 'date-time'}

    def test_with_default(self):
        field = fields.date_time(default='2014-08-25')
        assert field.__schema__ == {'type': 'string', 'format': 'date-time', 'default': '2014-08-25'}


class TestDateField(BaseFieldTestMixin, FieldTestCase):

    def field_class(self, **kwargs):
        return fields.date(**kwargs)

    def test_defaults(self):
        field = fields.date()
        assert not field.required
        assert field.__schema__ == {'type': 'string', 'format': 'date'}

    def test_with_default(self):
        field = fields.date(default='2014-08-25')
        assert field.__schema__ == {'type': 'string', 'format': 'date', 'default': '2014-08-25'}

class TestListField(BaseFieldTestMixin, FieldTestCase):

    def field_class(self, **kwargs):
        return fields.array(fields.string(), **kwargs)

    def test_defaults(self):
        field = fields.array(fields.string())
        assert not field.required
        assert field.__schema__ == {'type': 'array', 'items': {'type': 'string'}}

    def test_min_items(self):
        field = fields.array(fields.string(), min_items=5)
        assert 'minItems' in field.__schema__
        assert field.__schema__['minItems'] == 5

    def test_max_items(self):
        field = fields.array(fields.string(), max_items=42)
        assert 'maxItems' in field.__schema__
        assert field.__schema__['maxItems'] == 42

    def test_unique(self):
        field = fields.array(fields.string(), unique=True)
        assert 'uniqueItems' in field.__schema__
        assert field.__schema__['uniqueItems'] is True
