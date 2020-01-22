import json
from http import HTTPStatus

import pytest

import oapispec as oapi

from tests.mocks import mock_schema as mock_swagger_schema

@pytest.fixture
def mock_schema():
    """A mock schema packed and configured with every bit
    of possible data for testing on"""
    return mock_swagger_schema
