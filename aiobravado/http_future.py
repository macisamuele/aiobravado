# TODO: refactor bravado to define unmarshal_response_inner too
import sys

import six
import umsgpack
from bravado.exception import make_http_exception
from bravado.http_future import FutureAdapter
from bravado.http_future import HttpFuture
from bravado.http_future import raise_on_expected
from bravado.http_future import raise_on_unexpected
from bravado.http_future import reraise_errors
from bravado_core.content_type import APP_JSON
from bravado_core.content_type import APP_MSGPACK
from bravado_core.exception import MatchingResponseNotFound
from bravado_core.response import get_response_spec
from bravado_core.unmarshal import unmarshal_schema_object
from bravado_core.validate import validate_schema_object


class AIOFutureAdapter(FutureAdapter):
    """
    Mimics a :class:`concurrent.futures.Future` regardless of which client is
    performing the request, whether it is synchronous or actually asynchronous.

    This adapter must be implemented by all aiobravado clients such as FidoClient
    or RequestsClient to wrap the object returned by their 'request' method.
    """

    async def result(self, timeout=None):
        """
        Must implement a result method which blocks on result retrieval.

        :param timeout: maximum time to wait on result retrieval. Defaults to
            None which means blocking undefinitely.
        """
        raise NotImplementedError(
            "FutureAdapter must implement 'result' method"
        )


class AIOHttpFuture(HttpFuture):
    @reraise_errors
    async def result(self, timeout=None):
        """Blocking call to wait for the HTTP response.

        :param timeout: Number of seconds to wait for a response. Defaults to
            None which means wait indefinitely.
        :type timeout: float
        :return: Depends on the value of also_return_response sent in
            to the constructor.
        """
        inner_response = await self.future.result(timeout=timeout)
        incoming_response = self.response_adapter(inner_response)

        if self.operation is not None:
            await unmarshal_response(
                incoming_response,
                self.operation,
                self.response_callbacks)

            swagger_result = incoming_response.swagger_result
            if self.also_return_response:
                return swagger_result, incoming_response
            return swagger_result

        if 200 <= incoming_response.status_code < 300:
            return incoming_response

        raise make_http_exception(response=incoming_response)


async def unmarshal_response(incoming_response, operation, response_callbacks=None):
    """So the http_client is finished with its part of processing the response.
    This hands the response over to bravado_core for validation and
    unmarshalling and then runs any response callbacks. On success, the
    swagger_result is available as ``incoming_response.swagger_result``.

    :type incoming_response: :class:`bravado_core.response.IncomingResponse`
    :type operation: :class:`bravado_core.operation.Operation`
    :type response_callbacks: list of callable. See
        bravado_core.client.REQUEST_OPTIONS_DEFAULTS.

    :raises: HTTPError
        - On 5XX status code, the HTTPError has minimal information.
        - On non-2XX status code with no matching response, the HTTPError
            contains a detailed error message.
        - On non-2XX status code with a matching response, the HTTPError
            contains the return value.
    """
    response_callbacks = response_callbacks or []

    try:
        raise_on_unexpected(incoming_response)
        incoming_response.swagger_result = await unmarshal_response_inner(
            incoming_response,
            operation,
        )
    except MatchingResponseNotFound as e:
        exception = make_http_exception(
            response=incoming_response,
            message=str(e)
        )
        six.reraise(
            type(exception),
            exception,
            sys.exc_info()[2],
        )
    finally:
        # Always run the callbacks regardless of success/failure
        for response_callback in response_callbacks:
            response_callback(incoming_response, operation)

    raise_on_expected(incoming_response)


async def unmarshal_response_inner(response, op):
    """Unmarshal incoming http response into a value based on the
    response specification.

    :type response: :class:`bravado_core.response.IncomingResponse`
    :type op: :class:`bravado_core.operation.Operation`
    :returns: value where type(value) matches response_spec['schema']['type']
        if it exists, None otherwise.
    """
    deref = op.swagger_spec.deref
    response_spec = get_response_spec(response.status_code, op)

    def has_content(response_spec):
        return 'schema' in response_spec

    if not has_content(response_spec):
        return None

    content_type = response.headers.get('content-type', '').lower()

    if content_type.startswith(APP_JSON) or content_type.startswith(APP_MSGPACK):
        content_spec = deref(response_spec['schema'])
        if content_type.startswith(APP_JSON):
            content_value = await response.json()
        else:
            content_value = umsgpack.loads(await response.raw_bytes)
        if op.swagger_spec.config['validate_responses']:
            validate_schema_object(op.swagger_spec, content_spec, content_value)

        return unmarshal_schema_object(
            op.swagger_spec, content_spec, content_value)

    # TODO: Non-json response contents
    return response.text
