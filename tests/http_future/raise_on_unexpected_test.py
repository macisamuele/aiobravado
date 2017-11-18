import pytest
from bravado_core.response import IncomingResponse
from mock import Mock

from aiobravado.exception import HTTPError
from aiobravado.http_future import raise_on_unexpected


def test_5XX():
    http_response = Mock(spec=IncomingResponse, status_code=500)
    with pytest.raises(HTTPError) as excinfo:
        raise_on_unexpected(http_response)
    assert excinfo.value.response.status_code == 500


def test_non_5XX():
    http_response = Mock(spec=IncomingResponse, status_code=200)
    # no error raises == success
    raise_on_unexpected(http_response)
