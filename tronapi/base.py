import binascii
from abc import ABC

from tronapi.constants import DEFAULT_SOLIDITY_NODE, DEFAULT_TRON_NODE
from tronapi.provider import HttpProvider


class BaseTron(ABC):
    def __init__(self, full_node, solidity_node=None, event_server=None, private_key=None):
        """A Python API for interacting with the Tron (TRX)

        Args:
            full_node (:obj:`str`): A provider connected to a valid full node
            solidity_node (:obj:`str`): A provider connected to a valid solidity node
            event_server (:obj:`str`, optional): Optional for smart contract events. Expects a valid event server URL
            private_key (str): Optional default private key used when signing transactions

        """

        if not solidity_node:
            solidity_node = DEFAULT_SOLIDITY_NODE

        if isinstance(full_node, str):
            full_node = HttpProvider(full_node)

        if isinstance(solidity_node, str):
            solidity_node = HttpProvider(solidity_node)

        if isinstance(event_server, str):
            event_server = HttpProvider(event_server)

        self.__set_full_node(full_node)
        self.__set_solidity_node(solidity_node)
        self.__set_event_server(event_server)

        self.tron_node = HttpProvider(DEFAULT_TRON_NODE)

        if private_key:
            self.private_key = private_key

    def __set_full_node(self, provider):
        """Check specified "full node"

        Args:
            provider (HttpProvider): full node

        """
        if not self.is_valid_provider(provider):
            raise Exception('Invalid full node provided')

        self.full_node = provider
        self.full_node.status_page = '/wallet/getnowblock'

    def __set_solidity_node(self, provider):
        """Check specified "solidity node"

        Args:
            provider (HttpProvider): solidity node

        """
        if not self.is_valid_provider(provider):
            raise Exception('Invalid solidity node provided')

        self.solidity_node = provider
        self.solidity_node.status_page = '/walletsolidity/getnowblock'

    def __set_event_server(self, server):
        """Check specified "event server"

        Args:
            server (HttpProvider): event server

        """
        if server and not self.is_valid_provider(server):
            raise Exception('Invalid event provided')

        self.event_server = server

    def is_event_connected(self):
        """
        Checks if is connected to the event server.

        Returns:
            bool: True if successful, False otherwise.

        """
        if not self.event_server:
            return False

        return self.event_server.request('/healthcheck') == 'OK'

    @staticmethod
    def is_valid_provider(provider):
        """Check connected provider

        Args:
            provider(HttpProvider): Provider

        Returns:
           True if successful, False otherwise.

        """
        return isinstance(provider, HttpProvider)

    @staticmethod
    def to_ascii(s):
        return binascii.a2b_hex(s)

    @staticmethod
    def from_ascii(string):
        return binascii.b2a_hex(bytes(string, encoding="utf8"))

    @staticmethod
    def to_utf8(hex_string):
        return binascii.unhexlify(hex_string).decode('utf8')

    @staticmethod
    def from_utf8(string):
        return binascii.hexlify(bytes(string, encoding="utf8"))

    @staticmethod
    def from_decimal(value):
        return hex(value)

    @staticmethod
    def to_decimal(value):
        return int((str(value)), 10)

    def is_connected(self):
        """Check all connected nodes"""

        return {
            'full_node': self.full_node.is_connected(),
            'solidity_node': self.solidity_node.is_connected(),
            'event_server': self.is_event_connected()
        }
