import http
import logging
import urllib3
from eth_utils import to_dict
from urllib3 import get_host, HTTPConnectionPool, HTTPSConnectionPool
import json

from tronapi.exceptions import TronRequestError
from tronapi.utils.help import construct_user_agent

urllib3.disable_warnings()
LOGGER = logging.getLogger(__name__)


class TronResponse(object):
    """Encapsulates an http response from Tron."""

    def __init__(self, body=None, http_status=None, headers=None, call=None):
        """Initializes the object's internal data.
        Args:
            body (optional): The response body as text.
            http_status (optional): The http status code.
            headers (optional): The http headers.
            call (optional): The original call that was made.
        """
        self._body = body
        self._http_status = http_status
        self._headers = headers or {}
        self._call = call

        if self._http_status in (404, 502, 500):
            self._body = {
                'error': 'Request failed, try again'
            }

    def body(self):
        """Returns the response body."""
        return self._body

    def json(self):
        """Returns the response body -- in json if possible."""
        try:
            return json.loads(self._body)
        except (TypeError, ValueError):
            return self._body

    def headers(self):
        """Return the response headers."""
        return self._headers

    def etag(self):
        """Returns the ETag header value if it exists."""
        return self._headers.get('ETag')

    def status(self):
        """Returns the http status code of the response."""
        return self._http_status

    def is_success(self):
        """Returns boolean indicating if the call was successful."""
        if self._http_status == http.HTTPStatus.NOT_MODIFIED.value:
            # ETAG Hit
            return True
        elif self._http_status == http.HTTPStatus.OK.value:
            # HTTP Okay
            return True
        else:
            # Something else
            return False

    def is_failure(self):
        """Returns boolean indicating if the call failed."""
        return not self.is_success()

    def error(self):
        """
        Returns a TronRequestError (located in the exceptions module) with
        an appropriate debug message.
        """
        if self.is_failure():
            return TronRequestError(
                "Call was not successful",
                self._call,
                self.status(),
                self.headers(),
                self.body(),
            )
        else:
            return None


class HttpProvider(object):
    """Encapsulates session attributes and methods to make API calls."""

    logger = logging.getLogger(__name__)
    http_default_port = {
        'http': 80,
        'https': 443
    }

    http_scheme = {
        'http': HTTPConnectionPool,
        'https': HTTPSConnectionPool,
    }

    def __init__(self, host, request_kwargs=None):
        """Initializes the api instance."""

        self.host = host
        self._request_kwargs = request_kwargs or {}
        self._num_requests_succeeded = 0
        self._num_requests_attempted = 0
        self._status_page = None

        self.client = self.connect()

    def __str__(self):
        return "HTTP(S) connection {0}".format(self.host)

    @property
    def status_page(self):
        return self._status_page

    @status_page.setter
    def status_page(self, page):
        self._status_page = page

    @to_dict
    def get_request_kwargs(self):
        if 'headers' not in self._request_kwargs:
            yield 'headers', self.http_default_headers()
        if 'timeout' not in self._request_kwargs:
            yield 'timeout', 60
        for key, value in self._request_kwargs.items():
            yield key, value

    @staticmethod
    def http_default_headers():
        return {
            'content-type': 'application/json',
            'user-agent': construct_user_agent(),
        }

    def request(self, url, body=None, method='GET'):
        self.logger.debug("Making request HTTP. URI: %s, Path: %s",
                          self.host, url)
        method = method.lower()
        if method not in ['get', 'post']:
            raise Exception('The method is not defined')

        self._num_requests_attempted += 1
        if method == 'post':
            request = self.client.request(method=method, url=url, body=json.dumps(body))
        else:
            request = self.client.request(method=method, url=url, fields=body)

        data = TronResponse(body=request.data.decode('UTF-8'),
                            headers=request.headers,
                            http_status=request.status,
                            call={
                                'method': method,
                                'path': url,
                                'params': body,
                                **self.get_request_kwargs()
                            })

        if data.is_failure():
            raise data.error()

        response = data.json()
        if response == 'OK':
            response = dict({'status': 1})

        if isinstance(response, str):
            response = {}

        # We catch errors
        if 'Error' in response:
            raise ValueError(response['Error'])
        self._num_requests_succeeded += 1

        return response

    def connect(self):
        scheme, url, port = get_host(self.host)
        if port is None:
            port = self.http_default_port[scheme]

        pool_cls = self.http_scheme[scheme]
        client = pool_cls(host=url,
                          port=port,
                          **self.get_request_kwargs())

        return client

    def is_connected(self) -> bool:
        """Checking the connection from the connected node

        Returns:
            bool: True if successful, False otherwise.

        """
        response = self.request(self.status_page)
        if 'blockID' in response:
            return True
        elif 'status' in response:
            return True
        return False

    def get_num_requests_attempted(self):
        """Returns the number of calls attempted."""
        return self._num_requests_attempted

    def get_num_requests_succeeded(self):
        """Returns the number of calls that succeeded."""
        return self._num_requests_succeeded
