

from oapispec.schema import schema, meta


def test_schema_geneates_ui():
    sut = schema(handlers=None, metadata={
        'title': 'MOCK_SWAGGER_TITLE'
    })

    result = sut.generate_ui('http://MOCK_SPEC_URL')

    assert 'MOCK_SWAGGER_TITLE' in result
    assert 'http://MOCK_SPEC_URL' in result
