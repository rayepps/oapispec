# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import decimal
import six

from http import HTTPStatus
from collections import Hashable
from copy import deepcopy

from werkzeug.datastructures import MultiDict, FileStorage
from werkzeug import exceptions

from oapispec.core.errors import SpecsError
from oapispec.model import Model


#: Maps Flask-RESTX RequestParser locations to Swagger ones
LOCATIONS = {
    'args': 'query',
    'form': 'formData',
    'headers': 'header',
    'json': 'body',
    'values': 'query',
    'files': 'formData',
}

#: Maps Python primitives types to Swagger ones
PY_TYPES = {
    int: 'integer',
    str: 'string',
    bool: 'boolean',
    float: 'number',
    None: 'void'
}

SPLIT_CHAR = ','

text_type = lambda x: six.text_type(x)  # noqa


class Argument(object):
    '''
    :param name: Either a name or a list of option strings, e.g. foo or -f, --foo.
    :param default: The value produced if the argument is absent from the request.
    :param dest: The name of the attribute to be added to the object
        returned by :meth:`~reqparse.RequestParser.parse_args()`.
    :param bool required: Whether or not the argument may be omitted (optionals only).
    :param string action: The basic type of action to be taken when this argument
        is encountered in the request. Valid options are "store" and "append".
    :param bool ignore: Whether to ignore cases where the argument fails type conversion
    :param type: The type to which the request argument should be converted.
        If a type raises an exception, the message in the error will be returned in the response.
        Defaults to :class:`unicode` in python2 and :class:`str` in python3.
    :param location: The attributes of the :class:`flask.Request` object
        to source the arguments from (ex: headers, args, etc.), can be an
        iterator. The last item listed takes precedence in the result set.
    :param choices: A container of the allowable values for the argument.
    :param help: A brief description of the argument, returned in the
        response when the argument is invalid. May optionally contain
        an "{error_msg}" interpolation token, which will be replaced with
        the text of the error raised by the type converter.
    :param bool case_sensitive: Whether argument values in the request are
        case sensitive or not (this will convert all values to lowercase)
    :param bool store_missing: Whether the arguments default value should
        be stored if the argument is missing from the request.
    :param bool trim: If enabled, trims whitespace around the argument.
    :param bool nullable: If enabled, allows null value in argument.
    '''

    def __init__(self, name, default=None, dest=None, required=False,
                 ignore=False, type=text_type, location=('json', 'values',),
                 choices=(), action='store', help=None, operators=('=',),
                 case_sensitive=True, store_missing=True, trim=False,
                 nullable=True):
        self.name = name
        self.default = default
        self.dest = dest
        self.required = required
        self.ignore = ignore
        self.location = location
        self.type = type
        self.choices = choices
        self.action = action
        self.help = help
        self.case_sensitive = case_sensitive
        self.operators = operators
        self.store_missing = store_missing
        self.trim = trim
        self.nullable = nullable

    @property
    def __schema__(self):
        if self.location == 'cookie':
            return
        param = {
            'name': self.name,
            'in': LOCATIONS.get(self.location, 'query')
        }
        _handle_arg_type(self, param)
        if self.required:
            param['required'] = True
        if self.help:
            param['description'] = self.help
        if self.default is not None:
            param['default'] = self.default() if callable(self.default) else self.default
        if self.action == 'append':
            param['items'] = {'type': param['type']}
            param['type'] = 'array'
            param['collectionFormat'] = 'multi'
        if self.action == 'split':
            param['items'] = {'type': param['type']}
            param['type'] = 'array'
            param['collectionFormat'] = 'csv'
        if self.choices:
            param['enum'] = self.choices
            param['collectionFormat'] = 'multi'
        return param


class RequestParser(object):
    '''
    Enables adding and parsing of multiple arguments in the context of a single request.
    Ex::

        from flask_restx import RequestParser

        parser = RequestParser()
        parser.add_argument('foo')
        parser.add_argument('int_bar', type=int)
        args = parser.parse_args()

    :param bool trim: If enabled, trims whitespace on all arguments in this parser
    :param bool bundle_errors: If enabled, do not abort when first error occurs,
        return a dict with the name of the argument and the error message to be
        bundled and return all validation errors
    '''

    def __init__(self,
        argument_class=Argument,
        trim=False,
        bundle_errors=False):
        self.args = []
        self.argument_class = argument_class
        self.trim = trim
        self.bundle_errors = bundle_errors

    def add_argument(self, *args, **kwargs):
        '''
        Adds an argument to be parsed.

        Accepts either a single instance of Argument or arguments to be passed
        into :class:`Argument`'s constructor.

        See :class:`Argument`'s constructor for documentation on the available options.
        '''

        if len(args) == 1 and isinstance(args[0], self.argument_class):
            self.args.append(args[0])
        else:
            self.args.append(self.argument_class(*args, **kwargs))

        # Do not know what other argument classes are out there
        if self.trim and self.argument_class is Argument:
            # enable trim for appended element
            self.args[-1].trim = kwargs.get('trim', self.trim)

        return self

    def copy(self):
        '''Creates a copy of this RequestParser with the same set of arguments'''
        parser_copy = self.__class__(self.argument_class)
        parser_copy.args = deepcopy(self.args)
        parser_copy.trim = self.trim
        parser_copy.bundle_errors = self.bundle_errors
        return parser_copy

    @property
    def __schema__(self):
        params = []
        locations = set()
        for arg in self.args:
            param = arg.__schema__
            if param:
                params.append(param)
                locations.add(param['in'])
        if 'body' in locations and 'formData' in locations:
            raise SpecsError("Can't use formData and body at the same time")
        return params


def _handle_arg_type(arg, param):
    if isinstance(arg.type, Hashable) and arg.type in PY_TYPES:
        param['type'] = PY_TYPES[arg.type]
    elif hasattr(arg.type, '__apidoc__'):
        param['type'] = arg.type.__apidoc__['name']
        param['in'] = 'body'
    elif hasattr(arg.type, '__schema__'):
        param.update(arg.type.__schema__)
    elif arg.location == 'files':
        param['type'] = 'file'
    else:
        param['type'] = 'string'
