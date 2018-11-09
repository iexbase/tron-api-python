# --------------------------------------------------------------------------------------------
# Copyright (c) iEXBase. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import logging

from tronapi import HttpProvider
from tronapi.utils.types import is_string

STATUS_PAGE = {
    'full_node': '/wallet/getnowblock',
    'solidity_node': '/walletsolidity/getnowblock',
    'event_server': '/healthcheck'
}

DEFAULT_NODES = {
    'full_node': 'https://api.trongrid.io',
    'solidity_node': 'https://api.trongrid.io',
    'event_server': 'https://api.trongrid.io'
}


class TronManager(object):
    logger = logging.getLogger(__name__)
    _providers = None

    def __init__(self, tron, providers):
        self.tron = tron
        self.providers = providers
        self.preferred_node = None

        for key, value in self.providers.items():
            # Set the default node
            if not providers[key]:
                self.providers[key] = HttpProvider(DEFAULT_NODES[key])

            if is_string(value):
                self.providers[key] = HttpProvider(value)

            # Connection Test Path
            self.providers[key].status_page = STATUS_PAGE[key]

    @property
    def providers(self):
        return self._providers or tuple()

    @providers.setter
    def providers(self, value):
        self._providers = value

    @property
    def full_node(self) -> HttpProvider:
        if 'full_node' not in self.providers:
            raise ValueError('Full node is not activated.')
        return self.providers.get('full_node')

    @property
    def solidity_node(self) -> HttpProvider:
        if 'solidity_node' not in self.providers:
            raise ValueError('Solidity node is not activated.')
        return self.providers.get('solidity_node')

    @property
    def event_server(self) -> HttpProvider:
        if 'event_server' not in self.providers:
            raise ValueError('Event server is not activated.')

        return self.providers.get('event_server')

    def request(self, url, params=None, method='post'):
        # In this variable, we divide the resulting reference
        # into 2 parts to determine the type of node
        split = url[1:].split('/', 2)

        if split[0] in ('walletsolidity', 'walletextension'):
            return self.solidity_node.request(url, params, method)
        elif 'event' in split:
            return self.event_server.request(url, params, method)
        elif 'wallet' in split:
            return self.full_node.request(url, params, method)

        raise ValueError('Could not determine the type of node')

    def is_connected(self):
        is_node = dict()
        for key, value in self.providers.items():
            is_node.update({key: value.is_connected()})
        return is_node
