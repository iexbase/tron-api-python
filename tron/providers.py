from math import isnan

import urllib3
from urllib3 import get_host
import json


class HttpProvider:
    def __init__(self, host, timeout=30000, user=False, password=False, headers=None, status_page="/"):

        if headers is None:
            headers = {}

        self.host = host
        self.timeout = timeout
        self.user = user
        self.password = password
        self.headers = headers
        self.status_page = status_page

        # Разделяем хост
        scheme, base_url, port = get_host(host)

        if isnan(timeout) or timeout < 0:
            exit('Invalid timeout duration provided')

        if scheme == 'http':
            self.client = urllib3.HTTPConnectionPool(host=base_url, port=port, timeout=timeout, headers=headers)
        else:
            self.client = urllib3.HTTPSConnectionPool(host=base_url, port=port, timeout=timeout, headers=headers)

    def request(self, url, body=None, method='GET'):

        method = method.lower()

        if method not in ['get', 'post']:
            exit('The method is not defined')

        if method == 'post':
            response = self.client.request(method=method, url=url, body=json.dumps(body)).data.decode('utf-8')
        else:
            response = self.client.request(method=method, url=url, fields=body).data.decode('utf-8')

        return json.loads(response)
