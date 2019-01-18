# --------------------------------------------------------------------
# Copyright (c) iEXBase. All rights reserved.
# Licensed under the MIT License.
# See License.txt in the project root for license information.
# --------------------------------------------------------------------

"""
    tronapi.manager
    ===============

    This class is designed to configure and
    define nodes for different types.

    :copyright: © 2019 by the iEXBase.
    :license: MIT License
"""
from trx_utils import is_string

from tronapi import HttpProvider
from tronapi.constants import DEFAULT_NODES

# In this variable, you can specify the base paths
# to test the connection with the nodes.
# It is advisable to leave the settings unchanged.
STATUS_PAGE = {
    'full_node': '/wallet/getnowblock',
    'solidity_node': '/walletsolidity/getnowblock',
    'event_server': '/healthcheck'
}


class TronManager(object):
    """This class is designed to configure and define nodes
    for different types.

    """

    _providers = None

    def __init__(self, tron, providers):
        """Create new manager tron instance

        Args:
            tron: The tron implementation
            providers: List of providers

        """
        self.tron = tron
        self.providers = providers
        self.preferred_node = None

        for key, value in self.providers.items():
            # This condition checks the nodes,
            # if the link to the node is not specified,
            # we insert the default value to avoid an error.
            if not providers[key]:
                self.providers[key] = HttpProvider(DEFAULT_NODES[key])

            # If the type of the accepted provider is lower-case,
            # then we transform it to “HttpProvider”,
            if is_string(value):
                self.providers[key] = HttpProvider(value)
            self.providers[key].status_page = STATUS_PAGE[key]

    @property
    def providers(self):
        """Getting a list of all providers

        """
        return self._providers or tuple()

    @providers.setter
    def providers(self, value) -> None:
        """Add a new provider

        """
        self._providers = value

    @property
    def full_node(self) -> HttpProvider:
        """Getting and managing paths to a full node

        """
        if 'full_node' not in self.providers:
            raise ValueError('Full node is not activated.')
        return self.providers.get('full_node')

    @property
    def solidity_node(self) -> HttpProvider:
        """Getting and managing paths to a solidity node

        """
        if 'solidity_node' not in self.providers:
            raise ValueError('Solidity node is not activated.')
        return self.providers.get('solidity_node')

    @property
    def event_server(self) -> HttpProvider:
        """Getting and managing paths to a event server

        """
        if 'event_server' not in self.providers:
            raise ValueError('Event server is not activated.')
        return self.providers.get('event_server')

    def request(self, url, params=None, method=None):
        """Prepare and route the request object according to the manager's configuration.

        Args:
            url (str): Path to send
            params (dict): Options
            method (str): Request method

        """
        method = 'post' if method is None else method

        # In this variable, we divide the resulting reference
        # into 2 parts to determine the type of node
        split = url[1:].split('/', 2)

        if split[0] in ('walletsolidity', 'walletextension',):
            return self.solidity_node.request(url, json=params, method=method)
        elif split[0] in ('wallet',):
            return self.full_node.request(url, json=params, method=method)
        elif split[0] in ('event', 'healthcheck',):
            return self.event_server.request(url, json=params, method=method)

        raise ValueError('Could not determine the type of node')

    def is_connected(self):
        """Check connection with providers"""
        is_node = dict()
        for key, value in self.providers.items():
            is_node.update({key: value.is_connected()})
        return is_node
