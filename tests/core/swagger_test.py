

from oapispec.core.swagger import generate_swagger_ui


def test_generate_swagger_ui_inserts_arguments():
    result = generate_swagger_ui(
        spec_url='MOCK_SPEC_URL',
        asset_source='MOCK_ASSET_SOURCE',
        title='MOCK_TITLE')

    assert 'MOCK_SPEC_URL' in result
    assert 'MOCK_ASSET_SOURCE' in result
    assert 'MOCK_TITLE' in result

def test_generate_swagger_ui_inserts_defaults():
    result = generate_swagger_ui(spec_url='MOCK_SPEC_URL')

    assert 'MOCK_SPEC_URL' in result
    assert 'jsdelivr' in result
    assert 'Swagger UI' in result

def test_generate_swagger_ui_replaces_all_templates():
    result = generate_swagger_ui(spec_url='MOCK_SPEC_URL')

    assert '{{spec_url}}' not in result
    assert '{{asset_source}}' not in result
    assert '{{title}}' not in result
