import pytest
from bravado.requests_client import RequestsClient
from bravado_core.spec import Spec

from aiobravado.aiohttp_client import AsyncHttpClient
from aiobravado.client import SwaggerClient


@pytest.mark.parametrize(
    'http_client', [None, RequestsClient()]
)
def test_raise_if_http_client_in_not_async_raises_if_not_async_client(http_client):
    with pytest.raises(ValueError):
        SwaggerClient(
            swagger_spec=Spec.from_dict(
                spec_dict={},
                http_client=http_client,
                config={'validate_swagger_spec': False},
            ),
        )


@pytest.mark.parametrize(
    'http_client', [AsyncHttpClient()]
)
def test_raise_if_http_client_in_not_async_success(http_client):
    # Success if it does not raises
    SwaggerClient(
        swagger_spec=Spec.from_dict(
            spec_dict={},
            http_client=http_client,
            config={'validate_swagger_spec': False},
        ),
    )
