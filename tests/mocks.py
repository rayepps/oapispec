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
    'userId': oapi.fields.string(),
    'username': oapi.fields.string(required=True),
    'emailAddress': oapi.fields.string(required=True),
    'isEnabled': oapi.fields.boolean(),
    'phoneNumber': oapi.fields.string(),
    'userMetadata': oapi.fields.raw()
})

problem_details_model = oapi.model.Model('ProblemDetails', {
    'status': oapi.fields.integer(),
    'title': oapi.fields.string(),
    'detail': oapi.fields.string(),
    'type': oapi.fields.string(),
    'instance': oapi.fields.string(),
    'headers': oapi.fields.string()
})

paged_user_model = oapi.model.Model('PagedUserList', {
    'pageSize': oapi.fields.integer(),
    'pageNumber': oapi.fields.integer(),
    'total': oapi.fields.integer(),
    'users': oapi.fields.array(oapi.fields.nested(user_model))
})

search_arg_parser = oapi.parser()
search_arg_parser.add_argument('page_size', type=int, default=10, required=True, location='args')
search_arg_parser.add_argument('page_number', type=int, default=1, required=True, location='args')
search_arg_parser.add_argument('search_text', type=str, location='args')
search_arg_parser.add_argument('sort', type=str, location='args')

@oapi.doc.namespace('Health Check')
@oapi.doc.route('/ping')
@oapi.doc.method('GET')
@oapi.doc.response(HTTPStatus.CREATED, user_model)
@oapi.doc.response(HTTPStatus.UNAUTHORIZED, problem_details_model)
def ping():
    pass

@oapi.doc.namespace('User')
@oapi.doc.route('/user')
@oapi.doc.method('POST')
@oapi.doc.response(HTTPStatus.CREATED, user_model)
@oapi.doc.response(HTTPStatus.UNAUTHORIZED, problem_details_model)
@oapi.doc.expect(user_model)
def add_user():
    pass

@oapi.doc.namespace('User')
@oapi.doc.route('/user')
@oapi.doc.method('GET')
@oapi.doc.response(HTTPStatus.OK, paged_user_model)
@oapi.doc.response(HTTPStatus.UNAUTHORIZED, problem_details_model)
@oapi.doc.expect(search_arg_parser)
@oapi.doc.doc(args=search_arg_parser)
def get_users():
    pass

mock_schema = schema\
    .register(ping)\
    .register(add_user)\
    .register(get_users)
