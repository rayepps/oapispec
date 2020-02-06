# OpenAPI Spec Builder
Python library used to generate swagger docs from decorators. Doesn't screw with your requests, doesn't alter your middleware, doesn't put its dirty little hands where they don't belong. You decorate functions, register them on a schema, and generate a swagger doc.

## Install
Use `PyPI` -> `oapispec` @ https://pypi.org/project/oapispec

## Getting Started

In this example the `spec` resulted by generating the schema is a valid swagger dict/json spec that can be used in a swagger ui.
```
from http import HTTPStatus

import oapispec as oapi

schema = oapi.schema(metadata=dict(
    version='4.2.0',
    title='Super API'
))

@oapi.doc.namespace('Health Check')
@oapi.doc.route('/ping')
@oapi.doc.method('GET')
def ping():
    pass

spec = schema.register(ping).generate()
```

## Creating Models
In this example we create a model and use it as an expected parameter to a `POST` request.
```
book_model = oapi.model.Model('Book', {
    'title': oapi.fields.String(required=True),
    'author': oapi.fields.String(required=True),
    'yearWritten': oapi.fields.String,
    'genre': oapi.fields.String,
    'edition': oapi.fields.Integer,
    'isInPrint': oapi.fields.Boolean
})

@oapi.doc.namespace('Book')
@oapi.doc.route('/book')
@oapi.doc.method('POST')
@oapi.doc.response(HTTPStatus.CREATED.value, HTTPStatus.CREATED.description, book_model)
@oapi.doc.expect(book_model)
def add_book():
    pass

spec = schema.register(add_book).generate()
```

## Futher Examples
The best place to look is the `end_to_end` test in [tests/end_to_end_test.py](https://github.com/rayepps/oapispec/blob/develop/tests/end_to_end_test.py). This is always kept up to date as a strong example and test of what is possible. Note that you can see the expected output of a generated schema in [tests/assets/expected_full_schema_result.json](https://github.com/rayepps/oapispec/blob/develop/tests/assets/expected_full_schema_result.json). This can give you an idea of how the individual doc decorators work - both on their own and together - to produce the open api spec.
