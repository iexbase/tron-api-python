import codecs
from binascii import unhexlify

from eth_keys import keys


class Prefix:
    _prefix = '41'
    _pub_pref = '04'


class Address(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.hex = kwargs.get('hex')
        self.base58 = kwargs.get('base58')


class PrivateKey(Prefix):
    def __init__(self, private_key):
        """Work with private key.
        Getting: PublicKey, PublicToAddress

        Example:::
            PrivateKey("4d1bc37b069b9f2e975c37770b7c87185dc3a10454e3ea024ce1fce8f3eb78bf")
        """
        _private = unhexlify(bytes(private_key, encoding='utf8'))
        self._key = keys.PrivateKey(_private)

        # Key length must not exceed 64 length
        assert len(repr(self._key)) != 64

    @property
    def get_private(self):
        _raw_key = self._key.to_bytes()
        return codecs.decode(codecs.encode(_raw_key, 'hex'), 'ascii')

    @property
    def public_key(self) -> str:
        public_key = self._key.public_key.to_bytes()
        return self._pub_pref + codecs.decode(codecs.encode(public_key, 'hex'), 'ascii')

    @property
    def pubkey_to_address(self) -> str:
        public_key = self._key.public_key
        address = public_key.to_address()[2:]

        return self._prefix + address
