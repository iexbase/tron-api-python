import binascii
import math
from abc import ABC

import base58
from Crypto.Hash import keccak

from tronapi.provider import HttpProvider


class TronBase(ABC):
    def __set_full_node(self, provider) -> None:
        """Check specified "full node"

        Args:
            provider (HttpProvider): full node

        """
        if not self.is_valid_provider(provider):
            raise Exception('Invalid full node provided')

        self.full_node = provider
        self.full_node.status_page = '/wallet/getnowblock'

    def __set_solidity_node(self, provider) -> None:
        """Check specified "solidity node"

        Args:
            provider (HttpProvider): solidity node

        """
        if not self.is_valid_provider(provider):
            raise Exception('Invalid solidity node provided')

        self.solidity_node = provider
        self.solidity_node.status_page = '/walletsolidity/getnowblock'

    def __set_event_server(self, server) -> None:
        """Check specified "event server"

        Args:
            server (HttpProvider): event server

        """
        if server and not self.is_valid_provider(server):
            raise Exception('Invalid event provided')

        self.event_server = server

    def is_event_connected(self) -> bool:
        """
        Checks if is connected to the event server.

        Returns:
            bool: True if successful, False otherwise.

        """
        if not self.event_server:
            return False

        return self.event_server.request('/healthcheck') == 'OK'

    @staticmethod
    def is_valid_provider(provider) -> bool:
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

    @staticmethod
    def string_utf8_to_hex(name):
        """Convert a string to Hex format

        Args:
            name (str): string

        """
        return bytes(name, encoding='utf-8').hex()

    @staticmethod
    def to_tron(amount):
        """Convert float to trx format

        Args:
            amount (float): Value

        """
        return math.floor(amount * 1e6)

    @staticmethod
    def from_tron(amount):
        """Convert trx to float

        Args:
            amount (int): Value

        """
        return abs(amount) / 1e6

    @staticmethod
    def to_hex(address):
        """Helper function that will convert a generic value to hex

        Args:
            address (str): address

        """
        return base58.b58decode_check(address).hex().upper()

    @staticmethod
    def from_hex(address):
        """Helper function that will convert a generic value from hex

        Args:
            address (str): address

        """
        return base58.b58encode_check(bytes.fromhex(address))

    @staticmethod
    def sha3(string, prefix=False):
        """Helper function that will sha3 any value using keccak256

        Args:
            string (str): String to hash.
            prefix (bool): If true, adds '0x'

        """
        keccak_hash = keccak.new(digest_bits=256)
        keccak_hash.update(bytes(string, encoding='utf8'))

        if prefix:
            return '0x' + keccak_hash.hexdigest()

        return keccak_hash.hexdigest()

    def is_connected(self):
        """Check all connected nodes"""

        return {
            'full_node': self.full_node.is_connected(),
            'solidity_node': self.solidity_node.is_connected(),
            'event_server': self.is_event_connected()
        }
