import json, os, subprocess
from http import HTTPStatus

import pytest

from tests import utils

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

@oapi.doc.namespace('Health Check')
@oapi.doc.route('/ping')
@oapi.doc.method('GET')
@oapi.doc.response(HTTPStatus.CREATED, user_model)
@oapi.doc.response(HTTPStatus.UNAUTHORIZED, problem_details_model)
@oapi.doc.header('X-Tracking-Token')
def ping():
    pass

@oapi.doc.namespace('User')
@oapi.doc.route('/user')
@oapi.doc.method('POST')
@oapi.doc.response(HTTPStatus.CREATED, user_model)
@oapi.doc.response(HTTPStatus.UNAUTHORIZED, problem_details_model)
@oapi.doc.expect(user_model)
@oapi.doc.doc(security='apiKey')
def add_user():
    pass

@oapi.doc.namespace('User')
@oapi.doc.route('/user')
@oapi.doc.method('GET')
@oapi.doc.response(HTTPStatus.OK, paged_user_model)
@oapi.doc.response(HTTPStatus.UNAUTHORIZED, problem_details_model)
@oapi.doc.param('page_size', type=int, default=10, required=True, location='query')
@oapi.doc.param('page_number', type=int, default=1, required=True, location='query')
@oapi.doc.param('search_text', type=str, location='query')
@oapi.doc.param('sort', type=str, location='query')
@oapi.doc.param('refer', type=str, format='url', location='query')
@oapi.doc.param('email', type=str, format='email', location='query')
def get_users():
    pass

@oapi.doc.namespace('User')
@oapi.doc.route('/user/<str:user_id>')
@oapi.doc.method('GET')
@oapi.doc.response(HTTPStatus.OK, user_model)
@oapi.doc.response(HTTPStatus.UNAUTHORIZED, problem_details_model)
@oapi.doc.produces('xml')
@oapi.doc.deprecated
def find_user():
    pass

@oapi.doc.namespace('User')
@oapi.doc.route('/user/<str:user_id>')
@oapi.doc.method('PUT')
@oapi.doc.response(HTTPStatus.OK, user_model)
@oapi.doc.response(HTTPStatus.UNAUTHORIZED, problem_details_model)
@oapi.doc.vendor({ 'swagger-ui-color': 'black' })
def update_user():
    pass

@oapi.doc.hide
def grant_admin():
    pass


full_schema = schema\
    .register(ping)\
    .register(add_user)\
    .register(get_users)\
    .register(find_user)\
    .register(update_user)


def test_full_spec_generation():

    result = full_schema.generate()
    expected = utils.load_expected_full_schema_result()

    utils.write_result('end_to_end', json.dumps(result, indent=4))

    utils.diff(result, expected)

    assert result == expected


def test_full_spec_validation():
    '''Uses the swagger-cli command line tool to check that the output
    spec passes as a valid open api specification'''

    result = full_schema.generate()

    cmd_path = os.path.join(os.path.dirname(__file__), '../node_modules/.bin/swagger-cli')

    cmd = [cmd_path, 'validate', './tests/results/end_to_end.json']
    cmd_result = subprocess.check_output(cmd)

    assert 'is valid' in str(cmd_result)
