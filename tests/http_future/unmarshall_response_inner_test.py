# -*- coding: utf-8 -*-
from asyncio import coroutine

import mock
import msgpack
import pytest
from bravado_core.content_type import APP_JSON
from bravado_core.content_type import APP_MSGPACK
from bravado_core.response import IncomingResponse
from bravado_core.spec import Spec

from aiobravado.http_future import unmarshal_response_inner


@pytest.fixture
def empty_swagger_spec():
    return Spec(spec_dict={})


@pytest.fixture
def response_spec():
    return {
        'description': "Day of the week",
        'schema': {
            'type': 'string',
        }
    }


@pytest.fixture
def mock_get_response_spec():
    with mock.patch('aiobravado.http_future.get_response_spec') as m:
        yield m


@pytest.fixture
def mock_validate_schema_object():
    with mock.patch('aiobravado.http_future.validate_schema_object') as m:
        yield m


def test_no_content(mock_get_response_spec, empty_swagger_spec, event_loop):
    response_spec = {
        'description': "I don't have a 'schema' key so I return nothing",
    }
    response = mock.Mock(spec=IncomingResponse, status_code=200)

    mock_get_response_spec.return_value = response_spec
    op = mock.Mock(swagger_spec=empty_swagger_spec)
    result = event_loop.run_until_complete(unmarshal_response_inner(response, op))
    assert result is None


def test_json_content(mock_get_response_spec, empty_swagger_spec, response_spec, event_loop):
    response = mock.Mock(
        spec=IncomingResponse,
        status_code=200,
        headers={'content-type': APP_JSON},
        json=coroutine(mock.Mock(return_value='Monday')),
    )

    mock_get_response_spec.return_value = response_spec
    op = mock.Mock(swagger_spec=empty_swagger_spec)
    assert 'Monday' == event_loop.run_until_complete(unmarshal_response_inner(response, op))


def test_msgpack_content(mock_get_response_spec, empty_swagger_spec, response_spec, event_loop):
    message = 'Monday'
    response = mock.Mock(
        spec=IncomingResponse,
        status_code=200,
        headers={'content-type': APP_MSGPACK},
        raw_bytes=coroutine(lambda: msgpack.dumps(message))(),
    )

    mock_get_response_spec.return_value = response_spec
    op = mock.Mock(swagger_spec=empty_swagger_spec)
    assert message == event_loop.run_until_complete(unmarshal_response_inner(response, op))


def test_text_content(mock_get_response_spec, empty_swagger_spec, response_spec, event_loop):
    response = mock.Mock(
        spec=IncomingResponse,
        status_code=200,
        headers={'content-type': 'text/plain'},
        text='Monday',
    )

    mock_get_response_spec.return_value = response_spec
    op = mock.Mock(swagger_spec=empty_swagger_spec)
    assert 'Monday' == event_loop.run_until_complete(unmarshal_response_inner(response, op))


def test_skips_validation(
    mock_validate_schema_object,
    mock_get_response_spec,
    empty_swagger_spec,
    response_spec,
    event_loop,
):
    empty_swagger_spec.config['validate_responses'] = False
    response = mock.Mock(
        spec=IncomingResponse,
        status_code=200,
        headers={'content-type': APP_JSON},
        json=coroutine(mock.Mock(return_value='Monday')),
    )

    mock_get_response_spec.return_value = response_spec
    op = mock.Mock(swagger_spec=empty_swagger_spec)
    event_loop.run_until_complete(unmarshal_response_inner(response, op))
    assert mock_validate_schema_object.call_count == 0


def test_performs_validation(
    mock_validate_schema_object,
    mock_get_response_spec,
    empty_swagger_spec,
    response_spec,
    event_loop,
):
    empty_swagger_spec.config['validate_responses'] = True
    response = mock.Mock(
        spec=IncomingResponse,
        status_code=200,
        headers={'content-type': APP_JSON},
        json=coroutine(mock.Mock(return_value='Monday')),
    )

    mock_get_response_spec.return_value = response_spec
    op = mock.Mock(swagger_spec=empty_swagger_spec)
    event_loop.run_until_complete(unmarshal_response_inner(response, op))
    assert mock_validate_schema_object.call_count == 1
