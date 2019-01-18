# --------------------------------------------------------------------
# Copyright (c) iEXBase. All rights reserved.
# Licensed under the MIT License.
# See License.txt in the project root for license information.
# --------------------------------------------------------------------


"""
    tronapi.providers.http
    ======================

    Class for configuring http providers

    :copyright: © 2018 by the iEXBase.
    :license: MIT License
"""
import logging
from collections import namedtuple
from urllib.parse import urlparse

from eth_utils import to_dict
from requests import Session
from requests.exceptions import (
    ConnectionError as TrxConnectionError
)

from tronapi.common.encoding import to_text
from tronapi.providers.base import BaseProvider
from tronapi.exceptions import HTTP_EXCEPTIONS, TransportError

HTTP_SCHEMES = {'http', 'https'}
HttpResponse = namedtuple('HttpResponse', ('status_code', 'headers', 'data'))

log = logging.getLogger(__name__)


class HttpProvider(BaseProvider):
    """A Connection object to make HTTP requests to a particular node."""

    def __init__(self, node_url, request_kwargs=None):
        """Initializes a :class:`~tronapi.providers.http.HttpProvider`
        instance.

         Args:
            node_url (str):  Url of the node to connect to.
            request_kwargs (dict): Optional params to send with each request.

        """

        self.node_url = node_url.rstrip('/')
        uri = urlparse(node_url)
        # This condition checks the node that will connect
        # to work with methods.
        if uri.scheme not in HTTP_SCHEMES:
            raise NotImplementedError(
                'TronAPI does not know how to connect to scheme %r in %r' % (
                    uri.scheme,
                    self.node_url,
                )
            )

        self._request_kwargs = request_kwargs or {}
        self.session = Session()

    @to_dict
    def get_request_kwargs(self):
        """Header settings"""
        if 'headers' not in self._request_kwargs:
            yield 'headers', self._http_default_headers()
        for key, value in self._request_kwargs.items():
            yield key, value

    def request(self, path, json=None, params=None, method=None):
        """Performs an HTTP request with the given parameters.

           Args:
               path (str): API endpoint path (e.g.: ``'/transactions'``).
               json (dict): JSON data to send along with the request.
               params (dict): Dictionary of URL (query) parameters.
               method (str): HTTP method (e.g.: ``'GET'``).

        """
        try:
            response = self._request(
                method=method,
                url=self.node_url + path if path else self.node_url,
                json=json,
                params=params,
                **self.get_request_kwargs(),
            )
        except TrxConnectionError as err:
            raise err

        return response.data

    def is_connected(self) -> bool:
        """Connection check

        This method sends a test request to the connected node
        to determine its health.

        Returns:
            bool: True if successful,
            False otherwise.
        """
        response = self.request(path=self.status_page, method='get')
        if 'blockID' in response or response == 'OK':
            return True

        return False

    def _request(self, **kwargs):

        kwargs.setdefault('timeout', 60)

        response = self.session.request(**kwargs)
        text = response.text

        try:
            json = response.json()
        except ValueError:
            json = None

        if not (200 <= response.status_code < 300):
            exc_cls = HTTP_EXCEPTIONS.get(response.status_code, TransportError)
            raise exc_cls(response.status_code, text, json, kwargs.get('url'))

        data = json if json is not None else text
        log.debug(data)

        # Additional error interceptor that will occur in case of failed requests
        if 'Error' in data:
            raise ValueError(data['Error'])

        self.__error_manager(data)

        return HttpResponse(response.status_code, response.headers, data)

    @staticmethod
    def __error_manager(data):
        """Manager error

        Args:
            data (any): response data

        """
        # Additional error interceptor that will occur in case of failed requests
        if 'Error' in data:
            raise ValueError(data['Error'])

        # Convert hash errors
        if 'code' in data and 'message' in data:
            data['message'] = to_text(hexstr=data['message'])
