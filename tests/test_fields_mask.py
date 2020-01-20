
import json
import pytest

from collections import OrderedDict

from swaggerf.core import mask
from swaggerf.core.mask import Mask
from swaggerf import fields
from swaggerf.core.marshalling import marshal


def assert_data(tested, expected):
    '''Compare data without caring about order and type (dict vs. OrderedDict)'''
    tested = json.loads(json.dumps(tested))
    expected = json.loads(json.dumps(expected))
    assert tested == expected


class MaskMixin(object):

    def test_empty_mask(self):
        assert Mask('') == {}

    def test_one_field(self):
        assert Mask('field_name') == {'field_name': True}

    def test_multiple_field(self):
        mask = Mask('field1, field2, field3')
        assert_data(mask, {
            'field1': True,
            'field2': True,
            'field3': True,
        })

    def test_nested_fields(self):
        parsed = Mask('nested{field1,field2}')
        expected = {
            'nested': {
                'field1': True,
                'field2': True,
            }
        }
        assert parsed == expected

    def test_complex(self):
        parsed = Mask('field1, nested{field, sub{subfield}}, field2')
        expected = {
            'field1': True,
            'nested': {
                'field': True,
                'sub': {
                    'subfield': True,
                }
            },
            'field2': True,
        }
        assert_data(parsed, expected)

    def test_star(self):
        parsed = Mask('nested{field1,field2},*')
        expected = {
            'nested': {
                'field1': True,
                'field2': True,
            },
            '*': True,
        }
        assert_data(parsed, expected)

    def test_order(self):
        parsed = Mask('f_3, nested{f_1, f_2, f_3}, f_2, f_1')
        expected = OrderedDict([
            ('f_3', True),
            ('nested', OrderedDict([
                ('f_1', True),
                ('f_2', True),
                ('f_3', True),
            ])),
            ('f_2', True),
            ('f_1', True),
        ])
        assert parsed == expected

    def test_missing_closing_bracket(self):
        with pytest.raises(mask.ParseError):
            Mask('nested{')

    def test_consecutive_coma(self):
        with pytest.raises(mask.ParseError):
            Mask('field,,')

    def test_coma_before_bracket(self):
        with pytest.raises(mask.ParseError):
            Mask('field,{}')

    def test_coma_after_bracket(self):
        with pytest.raises(mask.ParseError):
            Mask('nested{,}')

    def test_unexpected_opening_bracket(self):
        with pytest.raises(mask.ParseError):
            Mask('{{field}}')

    def test_unexpected_closing_bracket(self):
        with pytest.raises(mask.ParseError):
            Mask('{field}}')

    def test_support_colons(self):
        assert Mask('field:name') == {'field:name': True}

    def test_support_dash(self):
        assert Mask('field-name') == {'field-name': True}

    def test_support_underscore(self):
        assert Mask('field_name') == {'field_name': True}


class TestMaskUnwrapped(MaskMixin):
    def parse(self, value):
        return Mask(value)


class TestMaskWrapped(MaskMixin):
    def parse(self, value):
        return Mask('{' + value + '}')


class DObject(object):
    '''A dead simple object built from a dictionnary (no recursion)'''
    def __init__(self, data):
        self.__dict__.update(data)


person_fields = {
    'name': fields.String,
    'age': fields.Integer
}


class TestApplyMask(object):
    def test_empty(self):
        data = {
            'integer': 42,
            'string': 'a string',
            'boolean': True,
        }
        result = mask.apply(data, '{}')
        assert result == {}

    def test_single_field(self):
        data = {
            'integer': 42,
            'string': 'a string',
            'boolean': True,
        }
        result = mask.apply(data, '{integer}')
        assert result == {'integer': 42}

    def test_multiple_fields(self):
        data = {
            'integer': 42,
            'string': 'a string',
            'boolean': True,
        }
        result = mask.apply(data, '{integer, string}')
        assert result == {'integer': 42, 'string': 'a string'}

    def test_star_only(self):
        data = {
            'integer': 42,
            'string': 'a string',
            'boolean': True,
        }
        result = mask.apply(data, '*')
        assert result == data

    def test_with_objects(self):
        data = DObject({
            'integer': 42,
            'string': 'a string',
            'boolean': True,
        })
        result = mask.apply(data, '{integer, string}')
        assert result == {'integer': 42, 'string': 'a string'}

    def test_with_ordered_dict(self):
        data = OrderedDict({
            'integer': 42,
            'string': 'a string',
            'boolean': True,
        })
        result = mask.apply(data, '{integer, string}')
        assert result == {'integer': 42, 'string': 'a string'}

    def test_nested_field(self):
        data = {
            'integer': 42,
            'string': 'a string',
            'boolean': True,
            'nested': {
                'integer': 42,
                'string': 'a string',
                'boolean': True,
            }
        }
        result = mask.apply(data, '{nested}')
        assert result == {'nested': {
            'integer': 42,
            'string': 'a string',
            'boolean': True,
        }}

    def test_nested_fields(self):
        data = {
            'nested': {
                'integer': 42,
                'string': 'a string',
                'boolean': True,
            }
        }
        result = mask.apply(data, '{nested{integer}}')
        assert result == {'nested': {'integer': 42}}

    def test_nested_with_start(self):
        data = {
            'nested': {
                'integer': 42,
                'string': 'a string',
                'boolean': True,
            },
            'other': 'value',
        }
        result = mask.apply(data, '{nested{integer},*}')
        assert result == {'nested': {'integer': 42}, 'other': 'value'}

    def test_nested_fields_when_none(self):
        data = {'nested': None}
        result = mask.apply(data, '{nested{integer}}')
        assert result == {'nested': None}

    def test_raw_api_fields(self):
        family_fields = {
            'father': fields.Raw,
            'mother': fields.Raw,
        }

        result = mask.apply(family_fields, 'father{name},mother{age}')

        data = {
            'father': {'name': 'John', 'age': 42},
            'mother': {'name': 'Jane', 'age': 42},
        }
        expected = {'father': {'name': 'John'}, 'mother': {'age': 42}}

        assert_data(marshal(data, result), expected)
        # Should leave th original mask untouched
        assert_data(marshal(data, family_fields), data)

    def test_nested_api_fields(self):
        family_fields = {
            'father': fields.Nested(person_fields),
            'mother': fields.Nested(person_fields),
        }

        result = mask.apply(family_fields, 'father{name},mother{age}')
        assert set(result.keys()) == set(['father', 'mother'])
        assert isinstance(result['father'], fields.Nested)
        assert set(result['father'].nested.keys()) == set(['name'])
        assert isinstance(result['mother'], fields.Nested)
        assert set(result['mother'].nested.keys()) == set(['age'])

        data = {
            'father': {'name': 'John', 'age': 42},
            'mother': {'name': 'Jane', 'age': 42},
        }
        expected = {'father': {'name': 'John'}, 'mother': {'age': 42}}

        assert_data(marshal(data, result), expected)
        # Should leave th original mask untouched
        assert_data(marshal(data, family_fields), data)

    def test_multiple_nested_api_fields(self):
        level_2 = {'nested_2': fields.Nested(person_fields)}
        level_1 = {'nested_1': fields.Nested(level_2)}
        root = {'nested': fields.Nested(level_1)}

        result = mask.apply(root, 'nested{nested_1{nested_2{name}}}')
        assert set(result.keys()) == set(['nested'])
        assert isinstance(result['nested'], fields.Nested)
        assert set(result['nested'].nested.keys()) == set(['nested_1'])

        data = {
            'nested': {
                'nested_1': {
                    'nested_2': {'name': 'John', 'age': 42}
                }
            }
        }
        expected = {
            'nested': {
                'nested_1': {
                    'nested_2': {'name': 'John'}
                }
            }
        }

        assert_data(marshal(data, result), expected)
        # Should leave th original mask untouched
        assert_data(marshal(data, root), data)

    def test_list_fields_with_simple_field(self):
        family_fields = {
            'name': fields.String,
            'members': fields.List(fields.String)
        }

        result = mask.apply(family_fields, 'members')
        assert set(result.keys()) == set(['members'])
        assert isinstance(result['members'], fields.List)
        assert isinstance(result['members'].container, fields.String)

        data = {'name': 'Doe', 'members': ['John', 'Jane']}
        expected = {'members': ['John', 'Jane']}

        assert_data(marshal(data, result), expected)
        # Should leave th original mask untouched
        assert_data(marshal(data, family_fields), data)

    def test_list_fields_with_nested(self):
        family_fields = {
            'members': fields.List(fields.Nested(person_fields))
        }

        result = mask.apply(family_fields, 'members{name}')
        assert set(result.keys()) == set(['members'])
        assert isinstance(result['members'], fields.List)
        assert isinstance(result['members'].container, fields.Nested)
        assert set(result['members'].container.nested.keys()) == set(['name'])

        data = {'members': [
            {'name': 'John', 'age': 42},
            {'name': 'Jane', 'age': 42},
        ]}
        expected = {'members': [{'name': 'John'}, {'name': 'Jane'}]}

        assert_data(marshal(data, result), expected)
        # Should leave th original mask untouched
        assert_data(marshal(data, family_fields), data)

    def test_list_fields_with_raw(self):
        family_fields = {
            'members': fields.List(fields.Raw)
        }

        result = mask.apply(family_fields, 'members{name}')

        data = {'members': [
            {'name': 'John', 'age': 42},
            {'name': 'Jane', 'age': 42},
        ]}
        expected = {'members': [{'name': 'John'}, {'name': 'Jane'}]}

        assert_data(marshal(data, result), expected)
        # Should leave th original mask untouched
        assert_data(marshal(data, family_fields), data)

    def test_list(self):
        data = [{
            'integer': 42,
            'string': 'a string',
            'boolean': True,
        }, {
            'integer': 404,
            'string': 'another string',
            'boolean': False,
        }]
        result = mask.apply(data, '{integer, string}')
        assert result == [
            {'integer': 42, 'string': 'a string'},
            {'integer': 404, 'string': 'another string'}
        ]

    def test_nested_list(self):
        data = {
            'integer': 42,
            'list': [{
                'integer': 42,
                'string': 'a string',
            }, {
                'integer': 404,
                'string': 'another string',
            }]
        }
        result = mask.apply(data, '{list}')
        assert result == {'list': [{
            'integer': 42,
            'string': 'a string',
        }, {
            'integer': 404,
            'string': 'another string',
        }]}

    def test_nested_list_fields(self):
        data = {
            'list': [{
                'integer': 42,
                'string': 'a string',
            }, {
                'integer': 404,
                'string': 'another string',
            }]
        }
        result = mask.apply(data, '{list{integer}}')
        assert result == {'list': [{'integer': 42}, {'integer': 404}]}

    def test_missing_field_none_by_default(self):
        result = mask.apply({}, '{integer}')
        assert result == {'integer': None}

    def test_missing_field_skipped(self):
        result = mask.apply({}, '{integer}', skip=True)
        assert result == {}

    def test_missing_nested_field_skipped(self):
        result = mask.apply({}, 'nested{integer}', skip=True)
        assert result == {}

    def test_mask_error_on_simple_fields(self):
        model = {
            'name': fields.String,
        }

        with pytest.raises(mask.MaskError):
            mask.apply(model, 'name{notpossible}')

    def test_mask_error_on_list_field(self):
        model = {
            'nested': fields.List(fields.String)
        }

        with pytest.raises(mask.MaskError):
            mask.apply(model, 'nested{notpossible}')
