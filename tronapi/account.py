import codecs
from binascii import unhexlify

import base58
import sha3
from ecdsa import SECP256k1, SigningKey
from eth_keys import KeyAPI

address_prefix = "41"
public_prefix = "04"


class Address(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.hex = kwargs.get('hex')
        self.base58 = kwargs.get('base58')

    def __str__(self):
        return self.hex


class GenerateAccount(object):

    def __init__(self):
        self._private = SigningKey.generate(curve=SECP256k1)

    def private_key(self):
        return self._private.to_string().hex()

    def public_key(self, is_hex=True):
        public_key = self._private.get_verifying_key().to_string()

        if is_hex:
            return public_prefix + public_key.hex()

        return public_key

    @property
    def address(self):
        keccak = sha3.keccak_256()
        keccak.update(self.public_key(False))
        address = keccak.hexdigest()[24:]
        address = address_prefix + address
        to_base58 = base58.b58encode_check(bytes.fromhex(address))

        return Address(base58=address, hex=to_base58.decode())


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
        return public_prefix + str(public_key)[2:]

    @property
    def address(self):
        public_key = self._key.public_key
        address = address_prefix + public_key.to_address()[2:]
        to_base58 = base58.b58encode_check(bytes.fromhex(address))
        return Address(base58=address, hex=to_base58.decode())

    def __str__(self):
        return self.private_key

    def __bytes__(self):
        return self._key.to_bytes()
