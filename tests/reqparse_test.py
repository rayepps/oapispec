
import decimal
import json
import six
import pytest

from werkzeug.exceptions import BadRequest
from werkzeug.wrappers import Request
from werkzeug.datastructures import FileStorage, MultiDict

from swaggerf.model import Model
from swaggerf import fields
from swaggerf.core import inputs
from swaggerf.core.errors import SpecsError
from swaggerf.core.reqparse import Argument, RequestParser


class MockRequest:
    def __init__(self, url, method=None, data=None, content_type=None, headers=None):
        self.unparsed_arguments = {}
        self.url = url
        self.method = method
        self.data = data
        self.content_type = content_type
        self.headers = headers


class TestReqParse(object):

    def test_chaining(self):
        parser = RequestParser()
        assert parser is parser.add_argument('foo')

    def test_request_parse_copy_including_settings(self):
        parser = RequestParser(trim=True, bundle_errors=True)
        parser_copy = parser.copy()

        assert parser.trim == parser_copy.trim
        assert parser.bundle_errors == parser_copy.bundle_errors

    def test_trim_request_parser_override_by_argument(self):
        parser = RequestParser(trim=True)
        parser.add_argument('foo', trim=False)

        assert parser.args[0].trim is False


class TestArgument(object):
    def test_name(self):
        arg = Argument('foo')
        assert arg.name == 'foo'

    def test_dest(self):
        arg = Argument('foo', dest='foobar')
        assert arg.dest == 'foobar'

    def test_location_url(self):
        arg = Argument('foo', location='url')
        assert arg.location == 'url'

    def test_location_url_list(self):
        arg = Argument('foo', location=['url'])
        assert arg.location == ['url']

    def test_location_header(self):
        arg = Argument('foo', location='headers')
        assert arg.location == 'headers'

    def test_location_json(self):
        arg = Argument('foo', location='json')
        assert arg.location == 'json'

    def test_location_get_json(self):
        arg = Argument('foo', location='get_json')
        assert arg.location == 'get_json'

    def test_location_header_list(self):
        arg = Argument('foo', location=['headers'])
        assert arg.location == ['headers']

    def test_type(self):
        arg = Argument('foo', type=int)
        assert arg.type == int

    def test_default(self):
        arg = Argument('foo', default=True)
        assert arg.default is True

    def test_default_help(self):
        arg = Argument('foo')
        assert arg.help is None

    def test_required(self):
        arg = Argument('foo', required=True)
        assert arg.required is True

    def test_ignore(self):
        arg = Argument('foo', ignore=True)
        assert arg.ignore is True

    def test_operator(self):
        arg = Argument('foo', operators=['>=', '<=', '='])
        assert arg.operators == ['>=', '<=', '=']

    def test_action_filter(self):
        arg = Argument('foo', action='filter')
        assert arg.action == 'filter'

    def test_action(self):
        arg = Argument('foo', action='append')
        assert arg.action == 'append'

    def test_choices(self):
        arg = Argument('foo', choices=[1, 2])
        assert arg.choices == [1, 2]

    def test_default_dest(self):
        arg = Argument('foo')
        assert arg.dest is None

    def test_default_operators(self):
        arg = Argument('foo')
        assert arg.operators[0] == '='
        assert len(arg.operators) == 1

    def test_default_default(self):
        arg = Argument('foo')
        assert arg.default is None

    def test_required_default(self):
        arg = Argument('foo')
        assert arg.required is False

    def test_ignore_default(self):
        arg = Argument('foo')
        assert arg.ignore is False

    def test_action_default(self):
        arg = Argument('foo')
        assert arg.action == 'store'

    def test_choices_default(self):
        arg = Argument('foo')
        assert len(arg.choices) == 0

    def test_option_case_sensitive(self):
        arg = Argument('foo', choices=['bar', 'baz'], case_sensitive=True)
        assert arg.case_sensitive is True

        # Insensitive
        arg = Argument('foo', choices=['bar', 'baz'], case_sensitive=False)
        assert arg.case_sensitive is False

        # Default
        arg = Argument('foo', choices=['bar', 'baz'])
        assert arg.case_sensitive is True


class TestRequestParserSchema(object):
    def test_empty_parser(self):
        parser = RequestParser()
        assert parser.__schema__ == []

    def test_primitive_types(self):
        parser = RequestParser()
        parser.add_argument('int', type=int, help='Some integer')
        parser.add_argument('str', type=str, help='Some string')
        parser.add_argument('float', type=float, help='Some float')

        assert parser.__schema__ == [
            {
                "description": "Some integer",
                "type": "integer",
                "name": "int",
                "in": "query"
            }, {
                "description": "Some string",
                "type": "string",
                "name": "str",
                "in": "query"
            }, {
                "description": "Some float",
                "type": "number",
                "name": "float",
                "in": "query"
            }
        ]

    def test_unknown_type(self):
        parser = RequestParser()
        parser.add_argument('unknown', type=lambda v: v)
        assert parser.__schema__ == [{
            'name': 'unknown',
            'type': 'string',
            'in': 'query',
        }]

    def test_required(self):
        parser = RequestParser()
        parser.add_argument('int', type=int, required=True)
        assert parser.__schema__ == [{
            'name': 'int',
            'type': 'integer',
            'in': 'query',
            'required': True,
        }]

    def test_default(self):
        parser = RequestParser()
        parser.add_argument('int', type=int, default=5)
        assert parser.__schema__ == [{
            'name': 'int',
            'type': 'integer',
            'in': 'query',
            'default': 5,
        }]

    def test_default_as_false(self):
        parser = RequestParser()
        parser.add_argument('bool', type=inputs.boolean, default=False)
        assert parser.__schema__ == [{
            'name': 'bool',
            'type': 'boolean',
            'in': 'query',
            'default': False,
        }]

    def test_choices(self):
        parser = RequestParser()
        parser.add_argument('string', type=str, choices=['a', 'b'])
        assert parser.__schema__ == [{
            'name': 'string',
            'type': 'string',
            'in': 'query',
            'enum': ['a', 'b'],
            'collectionFormat': 'multi',
        }]

    def test_location(self):
        parser = RequestParser()
        parser.add_argument('default', type=int)
        parser.add_argument('in_values', type=int, location='values')
        parser.add_argument('in_query', type=int, location='args')
        parser.add_argument('in_headers', type=int, location='headers')
        parser.add_argument('in_cookie', type=int, location='cookie')
        assert parser.__schema__ == [{
            'name': 'default',
            'type': 'integer',
            'in': 'query',
        }, {
            'name': 'in_values',
            'type': 'integer',
            'in': 'query',
        }, {
            'name': 'in_query',
            'type': 'integer',
            'in': 'query',
        }, {
            'name': 'in_headers',
            'type': 'integer',
            'in': 'header',
        }]

    def test_location_json(self):
        parser = RequestParser()
        parser.add_argument('in_json', type=str, location='json')
        assert parser.__schema__ == [{
            'name': 'in_json',
            'type': 'string',
            'in': 'body',
        }]

    def test_location_form(self):
        parser = RequestParser()
        parser.add_argument('in_form', type=int, location='form')
        assert parser.__schema__ == [{
            'name': 'in_form',
            'type': 'integer',
            'in': 'formData',
        }]

    def test_location_files(self):
        parser = RequestParser()
        parser.add_argument('in_files', type=FileStorage, location='files')
        assert parser.__schema__ == [{
            'name': 'in_files',
            'type': 'file',
            'in': 'formData',
        }]

    def test_form_and_body_location(self):
        parser = RequestParser()
        parser.add_argument('default', type=int)
        parser.add_argument('in_form', type=int, location='form')
        parser.add_argument('in_json', type=str, location='json')
        with pytest.raises(SpecsError) as cm:
            parser.__schema__

        assert cm.value.msg == "Can't use formData and body at the same time"

    def test_files_and_body_location(self):
        parser = RequestParser()
        parser.add_argument('default', type=int)
        parser.add_argument('in_files', type=FileStorage, location='files')
        parser.add_argument('in_json', type=str, location='json')
        with pytest.raises(SpecsError) as cm:
            parser.__schema__

        assert cm.value.msg == "Can't use formData and body at the same time"

    def test_models(self):
        todo_fields = Model('Todo', {
            'task': fields.String(required=True, description='The task details')
        })
        parser = RequestParser()
        parser.add_argument('todo', type=todo_fields)
        assert parser.__schema__ == [{
            'name': 'todo',
            'type': 'Todo',
            'in': 'body',
        }]

    def test_lists(self):
        parser = RequestParser()
        parser.add_argument('int', type=int, action='append')
        assert parser.__schema__ == [{
            'name': 'int',
            'in': 'query',
            'type': 'array',
            'collectionFormat': 'multi',
            'items': {'type': 'integer'}
        }]

    def test_split_lists(self):
        parser = RequestParser()
        parser.add_argument('int', type=int, action='split')
        assert parser.__schema__ == [{
            'name': 'int',
            'in': 'query',
            'type': 'array',
            'collectionFormat': 'csv',
            'items': {'type': 'integer'}
        }]

    def test_schema_interface(self):
        def custom(value):
            pass

        custom.__schema__ = {
            'type': 'string',
            'format': 'custom-format',
        }

        parser = RequestParser()
        parser.add_argument('custom', type=custom)

        assert parser.__schema__ == [{
            'name': 'custom',
            'in': 'query',
            'type': 'string',
            'format': 'custom-format',
        }]

    def test_callable_default(self):
        parser = RequestParser()
        parser.add_argument('int', type=int, default=lambda: 5)
        assert parser.__schema__ == [{
            'name': 'int',
            'type': 'integer',
            'in': 'query',
            'default': 5,
        }]
