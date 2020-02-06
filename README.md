# OpenAPI Spec Builder
Python library used to generate swagger docs from decorators. Doesn't screw with your requests, doesn't alter your middleware, doesn't put its dirty little hands where they don't belong. You decorate functions, register them on a schema, and generate a swagger doc.

## Install
Use `PyPI` -> `oapispec` @ https://pypi.org/project/oapispec

## Getting Started

In this very simplified example the `spec` resulted by generating the schema is a valid swagger dict/json spec that can be used in a swagger ui.
```py
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
where spec equals *vvv below vvv*. Using `oapispec` you can add many more details to your spec.
```json
{
    "swagger": "2.0",
    "basePath": "/",
    "paths": {
        "/ping": {
            "get": {
                "responses": {},
                "operationId": "ping",
                "tags": [
                    "Health Check"
                ]
            }
        }
    },
    "info": {
        "title": "Super API",
        "version": "4.2.0"
    },
    "produces": [
        "application/json"
    ],
    "consumes": [
        "application/json"
    ],
    "tags": [
        {
            "name": "Health Check"
        }
    ]
}

```

### Creating Models
In this example we create a model and use it as an expected parameter to a `POST` request.
```py
book_model = oapi.model.Model('Book', {
    'title': oapi.fields.string(required=True),
    'author': oapi.fields.string(required=True),
    'genre': oapi.fields.string(),
    'edition': oapi.fields.integer(),
    'isInPrint': oapi.fields.boolean()
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

### Futher Examples
The best place to look is the `end_to_end` test in [tests/end_to_end_test.py](https://github.com/rayepps/oapispec/blob/develop/tests/end_to_end_test.py). This is always kept up to date as a strong example and test of what is possible. Note that you can see the expected output of a generated schema in [tests/assets/expected_full_schema_result.json](https://github.com/rayepps/oapispec/blob/develop/tests/assets/expected_full_schema_result.json). This can give you an idea of how the doc decorators work - both on their own and together - to produce the open api spec.

## Contributions & Issues
Both are welcome and encouraged! For any problems your having add an issue in github. If your interested in contributing take a look at the [contributing doc](https://github.com/rayepps/oapispec/blob/develop/docs/CONTRIBUTING.md). If your interested in contributing you will probably want to know how to run/test/modify the project locally so checkout the [developing doc](https://github.com/rayepps/oapispec/blob/develop/docs/DEVELOPING.md)
