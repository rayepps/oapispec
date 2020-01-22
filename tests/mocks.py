from http import HTTPStatus

import oapispec as oapi


schema = oapi.schema(metadata=dict(
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

user_model = oapi.model.Model('User', {
    'userId': oapi.fields.String,
    'username': oapi.fields.String(required=True),
    'emailAddress': oapi.fields.String(required=True),
    'isEnabled': oapi.fields.Boolean,
    'phoneNumber': oapi.fields.String,
    'userMetadata': oapi.fields.Raw
})

problem_details_model = oapi.model.Model('ProblemDetails', {
    'status': oapi.fields.Integer,
    'title': oapi.fields.String,
    'detail': oapi.fields.String,
    'type': oapi.fields.String,
    'instance': oapi.fields.String,
    'headers': oapi.fields.String
})

paged_user_model = oapi.model.Model('PagedUserList', {
    'pageSize': oapi.fields.Integer,
    'pageNumber': oapi.fields.Integer,
    'total': oapi.fields.Integer,
    'users': oapi.fields.List(oapi.fields.Nested(user_model))
})

search_arg_parser = oapi.parser()
search_arg_parser.add_argument('page_size', type=int, default=10, required=True, location='args')
search_arg_parser.add_argument('page_number', type=int, default=1, required=True, location='args')
search_arg_parser.add_argument('search_text', type=str, location='args')
search_arg_parser.add_argument('sort', type=str, location='args')

@oapi.doc.namespace('Health Check')
@oapi.doc.route('/ping')
@oapi.doc.method('GET')
@oapi.doc.response(HTTPStatus.CREATED.value, HTTPStatus.CREATED.description, user_model)
@oapi.doc.response(HTTPStatus.UNAUTHORIZED.value, HTTPStatus.UNAUTHORIZED.description, problem_details_model)
def ping():
    pass

@oapi.doc.namespace('User')
@oapi.doc.route('/user')
@oapi.doc.method('POST')
@oapi.doc.response(HTTPStatus.CREATED.value, HTTPStatus.CREATED.description, user_model)
@oapi.doc.response(HTTPStatus.UNAUTHORIZED.value, HTTPStatus.UNAUTHORIZED.description, problem_details_model)
@oapi.doc.expect(user_model)
def add_user():
    pass

@oapi.doc.namespace('User')
@oapi.doc.route('/user')
@oapi.doc.method('GET')
@oapi.doc.response(HTTPStatus.OK.value, HTTPStatus.CREATED.description, paged_user_model)
@oapi.doc.response(HTTPStatus.UNAUTHORIZED.value, HTTPStatus.UNAUTHORIZED.description, problem_details_model)
@oapi.doc.expect(search_arg_parser)
@oapi.doc.doc(args=search_arg_parser)
def get_users():
    pass

mock_schema = schema\
    .register(ping)\
    .register(add_user)\
    .register(get_users)
