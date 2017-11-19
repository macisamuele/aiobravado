"""
The :class:`SwaggerClient` provides an interface for making API calls based on
a swagger spec, and returns responses of python objects which build from the
API response.

Structure Diagram::

        +---------------------+
        |                     |
        |    SwaggerClient    |
        |                     |
        +------+--------------+
               |
               |  has many
               |
        +------v--------------+
        |                     |
        |     Resource        +------------------+
        |                     |                  |
        +------+--------------+         has many |
               |                                 |
               |  has many                       |
               |                                 |
        +------v--------------+           +------v--------------+
        |                     |           |                     |
        |     Operation       |           |    SwaggerModel     |
        |                     |           |                     |
        +------+--------------+           +---------------------+
               |
               |  uses
               |
        +------v--------------+
        |                     |
        |     HttpClient      |
        |                     |
        +---------------------+


To get a client

.. code-block:: python

    client = aiobravado.client.SwaggerClient.from_url(swagger_spec_url)
"""
import logging

from bravado.client import CallableOperation  # noqa
from bravado.client import construct_params  # noqa
from bravado.client import construct_request  # noqa
from bravado.client import inject_headers_for_remote_refs
from bravado.client import marshal_param  # noqa
from bravado.client import ResourceDecorator  # noqa
from bravado.client import Spec  # noqa
from bravado.client import SwaggerClient as SyncSwaggerClient

from aiobravado.aiohttp_client import AsyncHttpClient
from aiobravado.swagger_model import AIOLoader

log = logging.getLogger(__name__)


def raise_if_http_client_in_not_async(http_client):
    if isinstance(http_client, AsyncHttpClient):
        raise ValueError(
            '{http_client_type} is not inheriting from {AsyncHttpClient_module}.AsyncHttpClient.\n'
            'Make sure to use a proper async HTTP client or consider to use bravado instead of aiobravado'.format(
                http_client_type=type(http_client),
                AsyncHttpClient_module=AsyncHttpClient.__module__,
            )
        )


class SwaggerClient(SyncSwaggerClient):
    def __init__(self, swagger_spec, also_return_response=False):
        """
        :param swagger_spec: bravado_core Spec object
        :type swagger_spec: bravado_core.spec.Spec
        :param also_return_response: return also raw response once result method is invoked
        :type also_return_response: bool
        """
        raise_if_http_client_in_not_async(swagger_spec.http_client)
        super(SwaggerClient, self).__init__(swagger_spec=swagger_spec, also_return_response=also_return_response)

    @classmethod
    async def from_url(cls, spec_url, http_client=None, request_headers=None, config=None):
        """Build a :class:`SwaggerClient` from a url to the Swagger
        specification for a RESTful API.

        :param spec_url: url pointing at the swagger API specification
        :type spec_url: str
        :param http_client: an HTTP client used to perform requests
        :type  http_client: :class:`bravado.http_client.HttpClient`
        :param request_headers: Headers to pass with http requests
        :type  request_headers: dict
        :param config: Config dict for aiobravado and bravado_core.
            See CONFIG_DEFAULTS in :module:`bravado_core.spec`.
            See CONFIG_DEFAULTS in :module:`aiobravado.client`.

        :rtype: :class:`bravado_core.spec.Spec`
        """
        log.debug('Loading from %s', spec_url)
        http_client = http_client or AsyncHttpClient()
        raise_if_http_client_in_not_async(http_client)
        loader = AIOLoader(http_client, request_headers=request_headers)
        spec_dict = await loader.load_spec(spec_url)

        # RefResolver may have to download additional json files (remote refs)
        # via http. Wrap http_client's request() so that request headers are
        # passed along with the request transparently. Yeah, this is not ideal,
        # but since RefResolver has new found responsibilities, it is
        # functional.
        if request_headers is not None:
            http_client.request = inject_headers_for_remote_refs(
                http_client.request, request_headers)

        return cls.from_spec(spec_dict, spec_url, http_client, config)
