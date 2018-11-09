# --------------------------------------------------------------------------------------------
# Copyright (c) iEXBase. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import logging
from eth_utils import to_dict
from urllib3 import get_host, HTTPConnectionPool, HTTPSConnectionPool, disable_warnings
import json

from tronapi.base.response import TronResponse
from tronapi.utils.help import (construct_user_agent)

disable_warnings()
LOGGER = logging.getLogger(__name__)


class HttpProvider:
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
        """Get the page to check the connection"""
        return self._status_page

    @status_page.setter
    def status_page(self, page):
        self._status_page = page

    @to_dict
    def get_request_kwargs(self):
        """Header settings"""
        if 'headers' not in self._request_kwargs:
            yield 'headers', self._http_default_headers()
        for key, value in self._request_kwargs.items():
            yield key, value

    @staticmethod
    def _http_default_headers():
        """Add default headers"""

        return {
            'content-type': 'application/json',
            'user-agent': construct_user_agent(),
            'timeout': 60
        }

    def request(self, url, body=None, method='GET'):
        """We send requests to nodes"""

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
        """HTTP provider configuration"""
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
        if 'blockID' in response or 'status' in response:
            return True

        return False

    def get_num_requests_attempted(self):
        """Returns the number of calls attempted."""
        return self._num_requests_attempted

    def get_num_requests_succeeded(self):
        """Returns the number of calls that succeeded."""
        return self._num_requests_succeeded
