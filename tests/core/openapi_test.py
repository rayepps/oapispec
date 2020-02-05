
import pytest

from tests import utils

from oapispec.core import openapi
from oapispec.core.utils import immutable

def make_mock_metadata(**overrides):
    return immutable({
        **{
            'title': 'mock title',
            'version': '1.0.0',
            'description': 'test mock api description',
            'terms_url': 'test mock terms url',
            'contact': 'test mock contact',
            'contact_email': 'mock@test.notreal',
            'contact_url': 'notreal.com/test/mock',
            'license': 'mock test license',
            'license_url': 'notreal.com/test/mock',
            'tags': ['mock', 'tag'],
            'representations': None,
            'authorizations': None,
            'security': None,
            'host': 'mock test host'
        },
        **overrides
    })

def test_base_path_patching():

    mock_metadata = make_mock_metadata(base_path='/')
    spec = openapi.create_openapi_spec_dict(mock_metadata, [])

    assert spec['basePath'] == '/'

    mock_metadata = make_mock_metadata(base_path='/path/to/place/')
    spec = openapi.create_openapi_spec_dict(mock_metadata, [])

    assert spec['basePath'] == '/path/to/place'

def test_extract_path_params():

    result = openapi.extract_path_params('/api/v1/boards/<string:board_id>/members/<int:member_id>')

    assert result['board_id']['name'] == 'board_id'
    assert result['board_id']['in'] == 'path'
    assert result['board_id']['required'] == True
    assert result['board_id']['type'] == 'string'

    assert result['member_id']['name'] == 'member_id'
    assert result['member_id']['in'] == 'path'
    assert result['member_id']['required'] == True
    assert result['member_id']['type'] == 'integer'

def test_extract_path_params_raises_unknown_type_exception():

    with pytest.raises(ValueError) as e_info:
        result = openapi.extract_path_params('/api/v1/boards/<date:board_id>')

def test_create_header_object():
    result = openapi.create_header_object('X-Mock-Header')
    assert result == { 'description': 'X-Mock-Header', 'type': 'string' }

    result = openapi.create_header_object({
        'type': int,
        'description': 'MOCK_HEADER_DESCRIPTION'
    })
    assert result == {
        'type': 'integer',
        'description': 'MOCK_HEADER_DESCRIPTION',
    }

    result = openapi.create_header_object({
        'type': [int],
        'description': 'MOCK_HEADER_DESCRIPTION'
    })
    assert result == {
        'type': 'array',
        'items': { 'type': 'integer' },
        'description': 'MOCK_HEADER_DESCRIPTION',
    }

    mock_mock = immutable(__schema__={
        'MOCK_KEY': 'MOCK_KEY_VALUE'
    })
    result = openapi.create_header_object({
        'type': mock_mock
    })
    assert result == {
        'type': mock_mock,
        'MOCK_KEY': 'MOCK_KEY_VALUE'
    }

def test_clean_route():

    route = openapi.clean_route('/path/to/<int:id>')
    assert route == '/path/to/{id}'

    route = openapi.clean_route('/path/to/<int:id>/other/<str:user_id_num>')
    assert route == '/path/to/{id}/other/{user_id_num}'


def test_expected_params():

    mock_apidoc = immutable(expect=[
        ('ProblemDetails', 'MOCK_DESCRIPTION')
    ])

    result = openapi.expected_params(mock_apidoc)
    expected = {
        'payload': {
            'name': 'payload',
            'required': True,
            'in': 'body',
            'schema': {
                '$ref': '#/definitions/ProblemDetails'
            },
            'description': 'MOCK_DESCRIPTION'
        }
    }

    assert result == expected

def test_get_operation_consumes():
    mock_parameters = [{
        'in': 'formData',
        'type': 'file'
    }]

    result = openapi.get_operation_consumes(mock_parameters)
    assert result == ['multipart/form-data']

    mock_parameters = [{
        'in': 'formData',
        'type': 'other'
    }]

    result = openapi.get_operation_consumes(mock_parameters)
    assert result == [
        'application/x-www-form-urlencoded',
        'multipart/form-data'
    ]

def test_parameters_for_throws_error_without_route():
    with pytest.raises(ValueError):
        openapi.parameters_for({})

# Done
