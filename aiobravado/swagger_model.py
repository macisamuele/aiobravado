import logging
import os
import os.path
from urllib.parse import urljoin
from urllib.parse import urlparse
from urllib.request import pathname2url

from bravado import swagger_model
from bravado.compat import json
from bravado_core.spec import is_yaml

from aiobravado.aiohttp_client import AiohttpClient

log = logging.getLogger(__name__)


def is_file_scheme_uri(url):
    return urlparse(url).scheme == 'file'


class AIOFileEventual(swagger_model.FileEventual):
    class FileResponse(object):

        def __init__(self, data):
            self._text = data
            self.headers = {}

        @property
        async def text(self):
            return self._text

        async def json(self):
            return json.loads(self._text.decode('utf-8'))

    async def result(self, *args, **kwargs):
        return self.wait(*args, **kwargs)


def request(http_client, url, headers):
    """Download and parse JSON from a URL.

    :param http_client: a :class:`bravado.http_client.HttpClient`
    :param url: url for api docs
    :return: an object with a :func`wait` method which returns the api docs
    """
    if is_file_scheme_uri(url):
        return AIOFileEventual(url)
    else:
        return swagger_model.request(http_client=http_client, url=url, headers=headers)


class AIOLoader(swagger_model.Loader):
    """
    AsyncIO Abstraction for loading Swagger API's.
    """

    async def load_spec(self, spec_url, base_url=None):
        """Load a Swagger Spec from the given URL

        :param spec_url: URL to swagger.json
        :param base_url: TODO: need this?
        :returns: json spec in dict form
        """
        response = await request(
            self.http_client,
            spec_url,
            self.request_headers,
        ).result()

        content_type = response.headers.get('content-type', '').lower()
        if is_yaml(spec_url, content_type):
            return self.load_yaml(await response.text)
        else:
            return await response.json()


# TODO: Adding the file scheme here just adds complexity to request()
# Is there a better way to handle this?
async def load_file(spec_file, http_client=None):
    """Loads a spec file

    :param spec_file: Path to swagger.json.
    :param http_client: HTTP client interface.
    :return: validated json spec in dict form
    :raise: IOError: On error reading swagger.json.
    """
    file_path = os.path.abspath(spec_file)
    url = urljoin('file:', pathname2url(file_path))
    # When loading from files, everything is relative to the spec file
    dir_path = os.path.dirname(file_path)
    base_url = urljoin('file:', pathname2url(dir_path))
    return await load_url(url, http_client=http_client, base_url=base_url)


async def load_url(spec_url, http_client=None, base_url=None):
    """Loads a Swagger spec.

    :param spec_url: URL for swagger.json.
    :param http_client: HTTP client interface.
    :param base_url:    Optional URL to be the base URL for finding API
                        declarations. If not specified, 'basePath' from the
                        resource listing is used.
    :return: validated spec in dict form
    :raise: IOError, URLError: On error reading api-docs.
    """
    if http_client is None:
        http_client = AiohttpClient()

    loader = AIOLoader(http_client=http_client)
    return await loader.load_spec(spec_url, base_url=base_url)
