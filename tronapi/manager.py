import logging
import re

from tronapi.provider import HttpProvider
from tronapi.utils.types import is_string

STATUS_PAGE = {
    'full_node': '/wallet/getnowblock',
    'solidity_node': '/walletsolidity/getnowblock'
}


class TronManager(object):
    logger = logging.getLogger(__name__)
    _providers = None

    def __init__(self, tron, providers):
        self.tron = tron
        self.providers = providers
        self.preferred_node = None

        for key, value in self.providers.items():
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

    def request(self, url, params=None, method='post'):

        if 'walletsolidity' or 'walletextension' in url[1:].split('/', 2):
            response = self.solidity_node.request(url, params, method)
        else:
            response = self.full_node.request(url, params, method)

        return response

    def is_connected(self) -> dict:
        is_node = dict()
        for key, value in self.providers.items():
            is_node.update({key: value.is_connected()})
        return is_node
