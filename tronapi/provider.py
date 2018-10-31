import http
import logging
from math import isnan
import tronapi
import urllib3
from urllib3 import get_host, HTTPConnectionPool, HTTPSConnectionPool
import json


from tronapi.exceptions import TronRequestError

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
        Returns a FacebookRequestError (located in the exceptions module) with
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

    http_default_headers = {
        'User-Agent': "tronapi-python-%s" % tronapi.__version__,
        'Content-Type': 'application/json'
    }

    port_defaults = {
        'http': 80,
        'https': 443
    }

    pool_classes_by_scheme = {
        'http': HTTPConnectionPool,
        'https': HTTPSConnectionPool,
    }

    def __init__(self, host,
                 timeout=60,
                 user=False,
                 password=False,
                 headers=None,
                 status_page='/wallet/getnowblock'):
        """Initializes the api instance."""
        if not headers:
            headers = {}

        headers.copy()
        headers.update(self.http_default_headers)

        self.host = host
        self.timeout = timeout
        self.user = user
        self.password = password
        self.headers = headers
        self.status_page = status_page
        self._num_requests_succeeded = 0
        self._num_requests_attempted = 0

        if isnan(timeout) or timeout < 0:
            raise Exception('Invalid timeout duration provided')

        self.client = self.connect()

    def request(self, url, body=None, method='GET'):
        method = method.lower()
        if method not in ['get', 'post']:
            raise Exception('The method is not defined')

        self._num_requests_attempted += 1

        if method == 'post':
            response = self.client.request(method=method, url=url, body=json.dumps(body))
        else:
            response = self.client.request(method=method, url=url, fields=body)

        data = TronResponse(body=response.data.decode('UTF-8'),
                            headers=response.headers,
                            http_status=response.status,
                            call={
                                'method': method,
                                'path': url,
                                'params': body,
                                'headers': self.headers
                            },
                            )

        if data.is_failure():
            raise data.error()

        self._num_requests_succeeded += 1
        return data.json()

    def connect(self):
        scheme, url, port = get_host(self.host)

        if port is None:
            port = self.port_defaults[scheme]

        pool_cls = self.pool_classes_by_scheme[scheme]
        client = pool_cls(host=url,
                          port=port,
                          timeout=self.timeout,
                          headers=self.headers)

        return client

    def is_connected(self):
        """Checking the connection from the connected node

        Returns:
            bool: True if successful, False otherwise.

        """
        response = self.request(self.status_page)

        return 'blockID' in response

    def get_num_requests_attempted(self):
        """Returns the number of calls attempted."""
        return self._num_requests_attempted

    def get_num_requests_succeeded(self):
        """Returns the number of calls that succeeded."""
        return self._num_requests_succeeded
