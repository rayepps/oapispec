
import pytest

from tests import utils

from oapispec import openapi


def test_swagger_end_to_end_on_mock_schema(mock_schema):

    sut = openapi.OpenApi(mock_schema.metadata, mock_schema.handlers)

    result = sut.as_dict()
    expected = utils.load_expected_mock_schema_result()

    assert result == expected
