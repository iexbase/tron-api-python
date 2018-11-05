import codecs
from binascii import unhexlify

import base58
import sha3
from ecdsa import SECP256k1, SigningKey
from eth_keys import KeyAPI

from tronapi.utils.hexadecimal import is_hex


class Address(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.hex = str(kwargs.get('hex'))
        self.base58 = str(kwargs.get('base58'))

    def __str__(self):
        return self.hex


class Account(object):

    def __init__(self):
        pass

    @staticmethod
    def from_hex(address):
        """Helper function that will convert a generic value from hex

        Args:
            address (str): address

        """
        if not is_hex(address):
            return address

        return base58.b58encode_check(bytes.fromhex(address))

    @staticmethod
    def to_hex(address):
        """Helper function that will convert a generic value to hex

        Args:
            address (str): address

        """
        if is_hex(address):
            return address.lower().replace('0x', '41', 2)

        return base58.b58decode_check(address).hex().upper()

    @staticmethod
    def from_private_key(private_key):
        return PrivateKey(private_key).address


class GenerateAccount(object):

    def __init__(self):
        self._private = SigningKey.generate(curve=SECP256k1)

    def private_key(self):
        return self._private.to_string().hex()

    def public_key(self, _is_hex=True):
        public_key = self._private.get_verifying_key().to_string()

        if _is_hex:
            return '04' + public_key.hex()

        return public_key

    @property
    def address(self):
        keccak = sha3.keccak_256()
        keccak.update(self.public_key(False))
        address = keccak.hexdigest()[24:]
        address = '41' + address
        to_base58 = base58.b58encode_check(bytes.fromhex(address))

        return Address(base58=address, hex=to_base58.decode())

    def __str__(self):
        return self.private_key().lower()


class PrivateKey(object):
    def __init__(self, private_key):
        """Work with private key.
        Getting: PublicKey, PublicToAddress

        Example:::
            PrivateKey("4d1bc37b069b9f2e975c37770b7c87185dc3a10454e3ea024ce1fce8f3eb78bf")
        """
        _private = unhexlify(bytes(private_key, encoding='utf8'))
        self._key = KeyAPI.PrivateKey(_private)

        # Key length must not exceed 64 length
        assert len(repr(self._key)) != 64

    @property
    def private_key(self):
        _raw_key = self._key.to_bytes()
        return codecs.decode(codecs.encode(_raw_key, 'hex'), 'ascii')

    @property
    def public_key(self) -> str:
        public_key = self._key.public_key
        return '04' + str(public_key)[2:]

    @property
    def address(self):
        public_key = self._key.public_key
        address = '41' + public_key.to_address()[2:]
        to_base58 = base58.b58encode_check(bytes.fromhex(address))

        return Address(hex=address, base58=to_base58.decode())

    def __str__(self):
        return self.private_key

    def __bytes__(self):
        return self._key.to_bytes()
