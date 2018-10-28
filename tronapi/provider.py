from math import isnan

import urllib3
from urllib3 import get_host
import json

urllib3.disable_warnings()


class HttpProvider:
    def __init__(self, host, timeout=30000, user=False, password=False, headers=None,
                 status_page='/wallet/getnowblock'):

        if headers is None:
            headers = {}

        self.host = host
        self.timeout = timeout
        self.user = user
        self.password = password
        self.headers = headers
        self.status_page = status_page

        # We share the host
        scheme, base_url, port = get_host(host)

        if isnan(timeout) or timeout < 0:
            raise Exception('Invalid timeout duration provided')

        if scheme == 'http':
            self.client = urllib3.HTTPConnectionPool(host=base_url, port=port, timeout=timeout, headers=headers)
        else:
            self.client = urllib3.HTTPSConnectionPool(host=base_url, port=port, timeout=timeout, headers=headers)

    def request(self, url, body=None, method='GET'):
        method = method.lower()
        if method not in ['get', 'post']:
            raise Exception('The method is not defined')

        if method == 'post':
            response = self.client.request(method=method, url=url, body=json.dumps(body)).data.decode('utf-8')
        else:
            response = self.client.request(method=method, url=url, fields=body).data.decode('utf-8')

        if response is None:
            return {'error': 'Empty response received'}

        if response == 'OK':
            return response

        return json.loads(response)

    def is_connected(self):
        """Checking the connection from the connected node

        Returns:
            bool: True if successful, False otherwise.

        """
        response = self.request(self.status_page)

        return 'blockID' in response
