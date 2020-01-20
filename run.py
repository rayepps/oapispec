from http import HTTPStatus
import json

import swaggerf as swag


schema = swag.schema(metadata=dict(
    version='2.0.0',
    title='Test API',
    description='The api I made',
    security='apikey',
    authorizations={
        'apikey': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization'
        }
    }
))

user_model = swag.model.Model('User', {
    'userId': swag.fields.String,
    'username': swag.fields.String(required=True),
    'emailAddress': swag.fields.String(required=True),
    'isEnabled': swag.fields.Boolean,
    'phoneNumber': swag.fields.String,
    'userMetadata': swag.fields.Raw
})

problem_details_model = swag.model.Model('ProblemDetails', {
    'status': swag.fields.Integer,
    'title': swag.fields.String,
    'detail': swag.fields.String,
    'type': swag.fields.String,
    'instance': swag.fields.String,
    'headers': swag.fields.String
})

paged_user_model = swag.model.Model('PagedUserList', {
    'pageSize': swag.fields.Integer,
    'pageNumber': swag.fields.Integer,
    'total': swag.fields.Integer,
    'users': swag.fields.List(swag.fields.Nested(user_model))
})

search_arg_parser = swag.parser()
search_arg_parser.add_argument('page_size', type=int, default=10, required=True, location='args')
search_arg_parser.add_argument('page_number', type=int, default=1, required=True, location='args')
search_arg_parser.add_argument('search_text', type=str, location='args')
search_arg_parser.add_argument('sort', type=str, location='args')

@swag.doc.namespace('Health Check')
@swag.doc.route('/ping')
@swag.doc.method('GET')
@swag.doc.response(HTTPStatus.CREATED.value, HTTPStatus.CREATED.description, user_model)
@swag.doc.response(HTTPStatus.UNAUTHORIZED.value, HTTPStatus.UNAUTHORIZED.description, problem_details_model)
def ping():
    pass

@swag.doc.namespace('User')
@swag.doc.route('/user')
@swag.doc.method('POST')
@swag.doc.response(HTTPStatus.CREATED.value, HTTPStatus.CREATED.description, user_model)
@swag.doc.response(HTTPStatus.UNAUTHORIZED.value, HTTPStatus.UNAUTHORIZED.description, problem_details_model)
@swag.doc.expect(user_model)
def add_user():
    pass

@swag.doc.namespace('User')
@swag.doc.route('/user')
@swag.doc.method('GET')
@swag.doc.response(HTTPStatus.OK.value, HTTPStatus.CREATED.description, paged_user_model)
@swag.doc.response(HTTPStatus.UNAUTHORIZED.value, HTTPStatus.UNAUTHORIZED.description, problem_details_model)
@swag.doc.expect(search_arg_parser)
@swag.doc.doc(args=search_arg_parser)
def get_users():
    pass

schema = schema\
    .register(ping)\
    .register(add_user)\
    .register(get_users)

swag_schema_dict = schema.generate()

##
## DEBUG - write to file
##

swag_schema_str = json.dumps(swag_schema_dict, sort_keys=True, indent=4)

with open("debug.json", "w") as json_file:
    json_file.write(swag_schema_str)
