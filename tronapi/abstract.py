import binascii
import math
from abc import ABC

import base58
from Crypto.Hash import keccak

from tronapi.provider import HttpProvider


class TronBase(ABC):

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
