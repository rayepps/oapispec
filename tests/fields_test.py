
from collections import OrderedDict
from datetime import date, datetime
from decimal import Decimal
from functools import partial

import pytz
import pytest

from oapispec import fields


class FieldTestCase(object):
    field_class = None

    def assert_field(self, field, value, expected):
        assert field.output('foo', {'foo': value}) == expected

    def assert_field_raises(self, field, value):
        with pytest.raises(fields.MarshallingError):
            field.output('foo', {'foo': value})


class BaseFieldTestMixin(object):
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


class NumberTestMixin(object):
    def test_min(self):
        field = self.field_class(min=0)
        assert 'minimum' in field.__schema__
        assert field.__schema__['minimum'] == 0
        assert 'exclusiveMinimum' not in field.__schema__

    def test_min_as_callable(self):
        field = self.field_class(min=lambda: 0)
        assert 'minimum' in field.__schema__
        assert field.__schema__['minimum'] == 0

    def test_min_exlusive(self):
        field = self.field_class(min=0, exclusiveMin=True)
        assert 'minimum' in field.__schema__
        assert field.__schema__['minimum'] == 0
        assert 'exclusiveMinimum' in field.__schema__
        assert field.__schema__['exclusiveMinimum'] is True

    def test_max(self):
        field = self.field_class(max=42)
        assert 'maximum' in field.__schema__
        assert field.__schema__['maximum'] == 42
        assert 'exclusiveMaximum' not in field.__schema__

    def test_max_as_callable(self):
        field = self.field_class(max=lambda: 42)
        assert 'maximum' in field.__schema__
        assert field.__schema__['maximum'] == 42

    def test_max_exclusive(self):
        field = self.field_class(max=42, exclusiveMax=True)
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
    field_class = fields.Raw

    def test_type(self):
        field = fields.Raw()
        assert field.__schema__['type'] == 'object'

    def test_default(self):
        field = fields.Raw(default='aaa')
        assert field.__schema__['default'] == 'aaa'
        self.assert_field(field, None, 'aaa')

    def test_default_as_callable(self):
        field = fields.Raw(default=lambda: 'aaa')
        assert field.__schema__['default'] == 'aaa'
        self.assert_field(field, None, 'aaa')

    def test_with_attribute(self):
        field = fields.Raw(attribute='bar')
        assert field.output('foo', {'bar': 42}) == 42

    def test_attribute_not_found(self):
        field = fields.Raw()
        assert field.output('foo', {'bar': 42}) is None


class TestStringField(StringTestMixin, BaseFieldTestMixin, FieldTestCase):
    field_class = fields.String

    def test_defaults(self):
        field = fields.String()
        assert not field.required
        assert not field.discriminator
        assert field.__schema__ == {'type': 'string'}

    def test_with_enum(self):
        enum = ['A', 'B', 'C']
        field = fields.String(enum=enum)
        assert not field.required
        assert field.__schema__ == {'type': 'string', 'enum': enum, 'example': enum[0]}

    def test_with_empty_enum(self):
        field = fields.String(enum=[])
        assert not field.required
        assert field.__schema__ == {'type': 'string'}

    def test_with_callable_enum(self):
        enum = lambda: ['A', 'B', 'C']  # noqa
        field = fields.String(enum=enum)
        assert not field.required
        assert field.__schema__ == {'type': 'string', 'enum': ['A', 'B', 'C'], 'example': 'A'}

    def test_with_empty_callable_enum(self):
        enum = lambda: []  # noqa
        field = fields.String(enum=enum)
        assert not field.required
        assert field.__schema__ == {'type': 'string'}

    def test_with_default(self):
        field = fields.String(default='aaa')
        assert field.__schema__ == {'type': 'string', 'default': 'aaa'}

    def test_string_field_with_discriminator(self):
        field = fields.String(discriminator=True)
        assert field.discriminator
        assert field.required
        assert field.__schema__ == {'type': 'string'}

    def test_string_field_with_discriminator_override_require(self):
        field = fields.String(discriminator=True, required=False)
        assert field.discriminator
        assert field.required
        assert field.__schema__ == {'type': 'string'}

    @pytest.mark.parametrize('value,expected', [
        ('string', 'string'),
        (42, '42'),
    ])
    def test_values(self, value, expected):
        self.assert_field(fields.String(), value, expected)


class TestIntegerField(BaseFieldTestMixin, NumberTestMixin, FieldTestCase):
    field_class = fields.Integer

    def test_defaults(self):
        field = fields.Integer()
        assert not field.required
        assert field.__schema__ == {'type': 'integer'}

    def test_with_default(self):
        field = fields.Integer(default=42)
        assert not field.required
        assert field.__schema__ == {'type': 'integer', 'default': 42}
        self.assert_field(field, None, 42)

    @pytest.mark.parametrize('value,expected', [
        (0, 0),
        (42, 42),
        ('42', 42),
        (None, None),
        (66.6, 66),
    ])
    def test_value(self, value, expected):
        self.assert_field(fields.Integer(), value, expected)

    def test_decode_error(self):
        field = fields.Integer()
        self.assert_field_raises(field, 'an int')


class TestBooleanField(BaseFieldTestMixin, FieldTestCase):
    field_class = fields.Boolean

    def test_defaults(self):
        field = fields.Boolean()
        assert not field.required
        assert field.__schema__ == {'type': 'boolean'}

    def test_with_default(self):
        field = fields.Boolean(default=True)
        assert not field.required
        assert field.__schema__ == {'type': 'boolean', 'default': True}

    @pytest.mark.parametrize('value,expected', [
        (True, True),
        (False, False),
        ({}, False),
        ('false', False),  # These consistent with inputs.boolean
        ('0', False),
    ])
    def test_value(self, value, expected):
        self.assert_field(fields.Boolean(), value, expected)


class TestFloatField(BaseFieldTestMixin, NumberTestMixin, FieldTestCase):
    field_class = fields.Float

    def test_defaults(self):
        field = fields.Float()
        assert not field.required
        assert field.__schema__ == {'type': 'number'}

    def test_with_default(self):
        field = fields.Float(default=0.5)
        assert not field.required
        assert field.__schema__ == {'type': 'number', 'default': 0.5}

    @pytest.mark.parametrize('value,expected', [
        ('-3.13', -3.13),
        (str(-3.13), -3.13),
        (3, 3.0),
    ])
    def test_value(self, value, expected):
        self.assert_field(fields.Float(), value, expected)

    def test_raises(self):
        self.assert_field_raises(fields.Float(), 'bar')

    def test_decode_error(self):
        field = fields.Float()
        self.assert_field_raises(field, 'not a float')


PI_STR = ('3.141592653589793238462643383279502884197169399375105820974944592307816406286208998628034825342117'
          '06798214808651328230664709384460955058223172535940812848111745028410270193852110555964462294895493'
          '038196442881097566593344612847564823378678316527120190914564856692346034861')

PI = Decimal(PI_STR)


class TestFixedField(BaseFieldTestMixin, NumberTestMixin, FieldTestCase):
    field_class = fields.Fixed

    def test_defaults(self):
        field = fields.Fixed()
        assert not field.required
        assert field.__schema__ == {'type': 'number'}

    def test_with_default(self):
        field = fields.Fixed(default=0.5)
        assert not field.required
        assert field.__schema__ == {'type': 'number', 'default': 0.5}

    def test_fixed(self):
        field5 = fields.Fixed(5)
        field4 = fields.Fixed(4)

        self.assert_field(field5, PI, '3.14159')
        self.assert_field(field4, PI, '3.1416')
        self.assert_field(field4, 3, '3.0000')
        self.assert_field(field4, '03', '3.0000')
        self.assert_field(field4, '03.0', '3.0000')

    def test_zero(self):
        self.assert_field(fields.Fixed(), '0', '0.00000')

    def test_infinite(self):
        field = fields.Fixed()
        self.assert_field_raises(field, '+inf')
        self.assert_field_raises(field, '-inf')

    def test_nan(self):
        field = fields.Fixed()
        self.assert_field_raises(field, 'NaN')


class TestArbitraryField(BaseFieldTestMixin, NumberTestMixin, FieldTestCase):
    field_class = fields.Arbitrary

    def test_defaults(self):
        field = fields.Arbitrary()
        assert not field.required
        assert field.__schema__ == {'type': 'number'}

    def test_with_default(self):
        field = fields.Arbitrary(default=0.5)
        assert field.__schema__ == {'type': 'number', 'default': 0.5}

    @pytest.mark.parametrize('value,expected', [
        (PI_STR, PI_STR),
        (PI, PI_STR),
    ])
    def test_value(self, value, expected):
        self.assert_field(fields.Arbitrary(), value, expected)


class TestDatetimeField(BaseFieldTestMixin, FieldTestCase):
    field_class = fields.DateTime

    def test_defaults(self):
        field = fields.DateTime()
        assert not field.required
        assert field.__schema__ == {'type': 'string', 'format': 'date-time'}
        self.assert_field(field, None, None)

    def test_with_default(self):
        field = fields.DateTime(default='2014-08-25')
        assert field.__schema__ == {'type': 'string', 'format': 'date-time', 'default': '2014-08-25T00:00:00'}
        self.assert_field(field, None, '2014-08-25T00:00:00')

    def test_with_default_as_datetime(self):
        field = fields.DateTime(default=datetime(2014, 8, 25))
        assert field.__schema__ == {'type': 'string', 'format': 'date-time', 'default': '2014-08-25T00:00:00'}
        self.assert_field(field, None, '2014-08-25T00:00:00')

    def test_with_default_as_date(self):
        field = fields.DateTime(default=date(2014, 8, 25))
        assert field.__schema__ == {'type': 'string', 'format': 'date-time', 'default': '2014-08-25T00:00:00'}
        self.assert_field(field, None, '2014-08-25T00:00:00')

    def test_min(self):
        field = fields.DateTime(min='1984-06-07T00:00:00')
        assert 'minimum' in field.__schema__
        assert field.__schema__['minimum'] == '1984-06-07T00:00:00'
        assert 'exclusiveMinimum' not in field.__schema__

    def test_min_as_date(self):
        field = fields.DateTime(min=date(1984, 6, 7))
        assert 'minimum' in field.__schema__
        assert field.__schema__['minimum'] == '1984-06-07T00:00:00'
        assert 'exclusiveMinimum' not in field.__schema__

    def test_min_as_datetime(self):
        field = fields.DateTime(min=datetime(1984, 6, 7, 1, 2, 0))
        assert 'minimum' in field.__schema__
        assert field.__schema__['minimum'] == '1984-06-07T01:02:00'
        assert 'exclusiveMinimum' not in field.__schema__

    def test_min_exlusive(self):
        field = fields.DateTime(min='1984-06-07T00:00:00', exclusiveMin=True)
        assert 'minimum' in field.__schema__
        assert field.__schema__['minimum'] == '1984-06-07T00:00:00'
        assert 'exclusiveMinimum' in field.__schema__
        assert field.__schema__['exclusiveMinimum'] is True

    def test_max(self):
        field = fields.DateTime(max='1984-06-07T00:00:00')
        assert 'maximum' in field.__schema__
        assert field.__schema__['maximum'] == '1984-06-07T00:00:00'
        assert 'exclusiveMaximum' not in field.__schema__

    def test_max_as_date(self):
        field = fields.DateTime(max=date(1984, 6, 7))
        assert 'maximum' in field.__schema__
        assert field.__schema__['maximum'] == '1984-06-07T00:00:00'
        assert 'exclusiveMaximum' not in field.__schema__

    def test_max_as_datetime(self):
        field = fields.DateTime(max=datetime(1984, 6, 7, 1, 2, 0))
        assert 'maximum' in field.__schema__
        assert field.__schema__['maximum'] == '1984-06-07T01:02:00'
        assert 'exclusiveMaximum' not in field.__schema__

    def test_max_exclusive(self):
        field = fields.DateTime(max='1984-06-07T00:00:00', exclusiveMax=True)
        assert 'maximum' in field.__schema__
        assert field.__schema__['maximum'] == '1984-06-07T00:00:00'
        assert 'exclusiveMaximum' in field.__schema__
        assert field.__schema__['exclusiveMaximum'] is True

    @pytest.mark.parametrize('value,expected', [
        (date(2011, 1, 1), 'Sat, 01 Jan 2011 00:00:00 -0000'),
        (datetime(2011, 1, 1), 'Sat, 01 Jan 2011 00:00:00 -0000'),
        (datetime(2011, 1, 1, 23, 59, 59),
         'Sat, 01 Jan 2011 23:59:59 -0000'),
        (datetime(2011, 1, 1, 23, 59, 59, tzinfo=pytz.utc),
         'Sat, 01 Jan 2011 23:59:59 -0000'),
        (datetime(2011, 1, 1, 23, 59, 59, tzinfo=pytz.timezone('CET')),
         'Sat, 01 Jan 2011 22:59:59 -0000')
    ])
    def test_rfc822_value(self, value, expected):
        self.assert_field(fields.DateTime(dt_format='rfc822'), value, expected)

    @pytest.mark.parametrize('value,expected', [
        (date(2011, 1, 1), '2011-01-01T00:00:00'),
        (datetime(2011, 1, 1), '2011-01-01T00:00:00'),
        (datetime(2011, 1, 1, 23, 59, 59),
         '2011-01-01T23:59:59'),
        (datetime(2011, 1, 1, 23, 59, 59, 1000),
         '2011-01-01T23:59:59.001000'),
        (datetime(2011, 1, 1, 23, 59, 59, tzinfo=pytz.utc),
         '2011-01-01T23:59:59+00:00'),
        (datetime(2011, 1, 1, 23, 59, 59, 1000, tzinfo=pytz.utc),
         '2011-01-01T23:59:59.001000+00:00'),
        (datetime(2011, 1, 1, 23, 59, 59, tzinfo=pytz.timezone('CET')),
         '2011-01-01T23:59:59+01:00')
    ])
    def test_iso8601_value(self, value, expected):
        self.assert_field(fields.DateTime(dt_format='iso8601'), value, expected)

    def test_unsupported_format(self):
        field = fields.DateTime(dt_format='raw')
        self.assert_field_raises(field, datetime.now())

    def test_unsupported_value_format(self):
        field = fields.DateTime(dt_format='raw')
        self.assert_field_raises(field, 'xxx')


class TestDateField(BaseFieldTestMixin, FieldTestCase):
    field_class = fields.Date

    def test_defaults(self):
        field = fields.Date()
        assert not field.required
        assert field.__schema__ == {'type': 'string', 'format': 'date'}

    def test_with_default(self):
        field = fields.Date(default='2014-08-25')
        assert field.__schema__ == {'type': 'string', 'format': 'date', 'default': '2014-08-25'}
        self.assert_field(field, None, '2014-08-25')

    def test_with_default_as_date(self):
        field = fields.Date(default=date(2014, 8, 25))
        assert field.__schema__ == {'type': 'string', 'format': 'date', 'default': '2014-08-25'}

    def test_with_default_as_datetime(self):
        field = fields.Date(default=datetime(2014, 8, 25))
        assert field.__schema__ == {'type': 'string', 'format': 'date', 'default': '2014-08-25'}

    def test_min(self):
        field = fields.Date(min='1984-06-07')
        assert 'minimum' in field.__schema__
        assert field.__schema__['minimum'] == '1984-06-07'
        assert 'exclusiveMinimum' not in field.__schema__

    def test_min_as_date(self):
        field = fields.Date(min=date(1984, 6, 7))
        assert 'minimum' in field.__schema__
        assert field.__schema__['minimum'] == '1984-06-07'
        assert 'exclusiveMinimum' not in field.__schema__

    def test_min_as_datetime(self):
        field = fields.Date(min=datetime(1984, 6, 7, 1, 2, 0))
        assert 'minimum' in field.__schema__
        assert field.__schema__['minimum'] == '1984-06-07'
        assert 'exclusiveMinimum' not in field.__schema__

    def test_min_exlusive(self):
        field = fields.Date(min='1984-06-07', exclusiveMin=True)
        assert 'minimum' in field.__schema__
        assert field.__schema__['minimum'] == '1984-06-07'
        assert 'exclusiveMinimum' in field.__schema__
        assert field.__schema__['exclusiveMinimum'] is True

    def test_max(self):
        field = fields.Date(max='1984-06-07')
        assert 'maximum' in field.__schema__
        assert field.__schema__['maximum'] == '1984-06-07'
        assert 'exclusiveMaximum' not in field.__schema__

    def test_max_as_date(self):
        field = fields.Date(max=date(1984, 6, 7))
        assert 'maximum' in field.__schema__
        assert field.__schema__['maximum'] == '1984-06-07'
        assert 'exclusiveMaximum' not in field.__schema__

    def test_max_as_datetime(self):
        field = fields.Date(max=datetime(1984, 6, 7, 1, 2, 0))
        assert 'maximum' in field.__schema__
        assert field.__schema__['maximum'] == '1984-06-07'
        assert 'exclusiveMaximum' not in field.__schema__

    def test_max_exclusive(self):
        field = fields.Date(max='1984-06-07', exclusiveMax=True)
        assert 'maximum' in field.__schema__
        assert field.__schema__['maximum'] == '1984-06-07'
        assert 'exclusiveMaximum' in field.__schema__
        assert field.__schema__['exclusiveMaximum'] is True

    @pytest.mark.parametrize('value,expected', [
        (date(2011, 1, 1), '2011-01-01'),
        (datetime(2011, 1, 1), '2011-01-01'),
        (datetime(2011, 1, 1, 23, 59, 59), '2011-01-01'),
        (datetime(2011, 1, 1, 23, 59, 59, 1000), '2011-01-01'),
        (datetime(2011, 1, 1, 23, 59, 59, tzinfo=pytz.utc), '2011-01-01'),
        (datetime(2011, 1, 1, 23, 59, 59, 1000, tzinfo=pytz.utc), '2011-01-01'),
        (datetime(2011, 1, 1, 23, 59, 59, tzinfo=pytz.timezone('CET')), '2011-01-01')
    ])
    def test_value(self, value, expected):
        self.assert_field(fields.Date(), value, expected)

    def test_unsupported_value_format(self):
        self.assert_field_raises(fields.Date(), 'xxx')


class TestFormatedStringField(StringTestMixin, BaseFieldTestMixin, FieldTestCase):
    field_class = partial(fields.FormattedString, 'Hello {name}')

    def test_defaults(self):
        field = fields.FormattedString('Hello {name}')
        assert not field.required
        assert field.__schema__ == {'type': 'string'}

    def test_dict(self):
        data = {
            'sid': 3,
            'account_sid': 4,
        }
        field = fields.FormattedString('/foo/{account_sid}/{sid}/')
        assert field.output('foo', data) == '/foo/4/3/'

    def test_none(self):
        field = fields.FormattedString('{foo}')
        # self.assert_field_raises(field, None)
        with pytest.raises(fields.MarshallingError):
            field.output('foo', None)

    def test_invalid_object(self):
        field = fields.FormattedString('/foo/{0[account_sid]}/{0[sid]}/')
        self.assert_field_raises(field, {})

    def test_tuple(self):
        field = fields.FormattedString('/foo/{0[account_sid]}/{0[sid]}/')
        self.assert_field_raises(field, (3, 4))

class TestListField(BaseFieldTestMixin, FieldTestCase):
    field_class = partial(fields.List, fields.String)

    def test_defaults(self):
        field = fields.List(fields.String)
        assert not field.required
        assert field.__schema__ == {'type': 'array', 'items': {'type': 'string'}}

    def test_min_items(self):
        field = fields.List(fields.String, min_items=5)
        assert 'minItems' in field.__schema__
        assert field.__schema__['minItems'] == 5

    def test_max_items(self):
        field = fields.List(fields.String, max_items=42)
        assert 'maxItems' in field.__schema__
        assert field.__schema__['maxItems'] == 42

    def test_unique(self):
        field = fields.List(fields.String, unique=True)
        assert 'uniqueItems' in field.__schema__
        assert field.__schema__['uniqueItems'] is True

    @pytest.mark.parametrize('value,expected', [
        (['a', 'b', 'c'], ['a', 'b', 'c']),
        (['c', 'b', 'a'], ['c', 'b', 'a']),
        (('a', 'b', 'c'), ['a', 'b', 'c']),
        (['a'], ['a']),
        (None, None),
    ])
    def test_value(self, value, expected):
        self.assert_field(fields.List(fields.String()), value, expected)

    def test_with_set(self):
        field = fields.List(fields.String)
        value = set(['a', 'b', 'c'])
        output = field.output('foo', {'foo': value})
        assert set(output) == value

    def test_with_scoped_attribute_on_dict_or_obj(self):
        class Test(object):
            def __init__(self, data):
                self.data = data

        class Nested(object):
            def __init__(self, value):
                self.value = value

        nesteds = [Nested(i) for i in ['a', 'b', 'c']]
        test_obj = Test(nesteds)
        test_dict = {'data': [{'value': 'a'}, {'value': 'b'}, {'value': 'c'}]}

        field = fields.List(fields.String(attribute='value'), attribute='data')
        assert ['a' == 'b', 'c'], field.output('whatever', test_obj)
        assert ['a' == 'b', 'c'], field.output('whatever', test_dict)

    def test_with_attribute(self):
        data = [{'a': 1, 'b': 1}, {'a': 2, 'b': 1}, {'a': 3, 'b': 1}]
        field = fields.List(fields.Integer(attribute='a'))
        self.assert_field(field, data, [1, 2, 3])

    def test_list_of_raw(self):
        field = fields.List(fields.Raw)

        data = [{'a': 1, 'b': 1}, {'a': 2, 'b': 1}, {'a': 3, 'b': 1}]
        expected = [OrderedDict([('a', 1), ('b', 1)]),
                    OrderedDict([('a', 2), ('b', 1)]),
                    OrderedDict([('a', 3), ('b', 1)])]
        self.assert_field(field, data, expected)

        data = [1, 2, 'a']
        self.assert_field(field, data, data)


class TestWildcardField(BaseFieldTestMixin, FieldTestCase):
    field_class = partial(fields.Wildcard, fields.String)

    def test_types(self):
        with pytest.raises(fields.MarshallingError):
            class WrongType:
                pass
            x = WrongType()
            field1 = fields.Wildcard(WrongType)  # noqa
            field2 = fields.Wildcard(x)  # noqa

    def test_defaults(self):
        field = fields.Wildcard(fields.String)
        assert not field.required
        assert field.__schema__ == {'type': 'object', 'additionalProperties': {'type': 'string'}}

    def test_with_scoped_attribute_on_dict_or_obj(self):
        class Test(object):
            def __init__(self, data):
                self.data = data

        class Nested(object):
            def __init__(self, value):
                self.value = value

        nesteds = [Nested(i) for i in ['a', 'b', 'c']]
        test_obj = Test(nesteds)
        test_dict = {'data': [{'value': 'a'}, {'value': 'b'}, {'value': 'c'}]}

        field = fields.Wildcard(fields.String(attribute='value'), attribute='data')
        assert ['a' == 'b', 'c'], field.output('whatever', test_obj)
        assert ['a' == 'b', 'c'], field.output('whatever', test_dict)

    def test_list_of_raw(self):
        field = fields.Wildcard(fields.Raw)

        data = [{'a': 1, 'b': 1}, {'a': 2, 'b': 1}, {'a': 3, 'b': 1}]
        expected = [OrderedDict([('a', 1), ('b', 1)]),
                    OrderedDict([('a', 2), ('b', 1)]),
                    OrderedDict([('a', 3), ('b', 1)])]
        self.assert_field(field, data, expected)

        data = [1, 2, 'a']
        self.assert_field(field, data, data)

class TestClassNameField(StringTestMixin, BaseFieldTestMixin, FieldTestCase):
    field_class = fields.ClassName

    def test_simple_string_field(self):
        field = fields.ClassName()
        assert not field.required
        assert not field.discriminator
        assert field.__schema__ == {'type': 'string'}

class TestCustomField(FieldTestCase):
    def test_custom_field(self):
        class CustomField(fields.Integer):
            __schema_format__ = 'int64'

        field = CustomField()

        assert field.__schema__ == {'type': 'integer', 'format': 'int64'}


class TestFieldsHelpers(object):
    def test_to_dict(self):
        expected = data = {'foo': 42}
        assert fields.to_marshallable_type(data) == expected

    def test_to_dict_obj(self):
        class Foo(object):
            def __init__(self):
                self.foo = 42
        expected = {'foo': 42}
        assert fields.to_marshallable_type(Foo()) == expected

    def test_to_dict_custom_marshal(self):
        class Foo(object):
            def __marshallable__(self):
                return {'foo': 42}
        expected = {'foo': 42}
        assert fields.to_marshallable_type(Foo()) == expected

    def test_get_value(self):
        assert fields.get_value('foo', {'foo': 42}) == 42

    def test_get_value_no_value(self):
        assert fields.get_value("foo", {'foo': 42}) == 42

    def test_get_value_indexable_object(self):
        class Test(object):
            def __init__(self, value):
                self.value = value

            def __getitem__(self, n):
                if type(n) is int:
                    if n < 3:
                        return n
                    raise IndexError
                raise TypeError

        obj = Test('hi')
        assert fields.get_value('value', obj) == 'hi'