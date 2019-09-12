# --------------------------------------------------------------------
# Copyright (c) iEXBase. All rights reserved.
# Licensed under the MIT License.
# See License.txt in the project root for license information.
# --------------------------------------------------------------------

import codecs
from binascii import unhexlify

import base58
import ecdsa
from eth_keys import KeyAPI
from eth_account import Account as ETHAccount
from trx_utils import is_hex, is_bytes

from tronapi.common.datastructures import AttributeDict


class Account:
    @staticmethod
    def create():
        generate_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        return PrivateKey(generate_key.to_string().hex())

    @staticmethod
    def sign_hash(message_hash, private_key):
        if not is_hex(message_hash):
            raise ValueError('Invalid message_hash provided')

        return ETHAccount.signHash(message_hash, private_key)

    @staticmethod
    def recover_hash(message_hash, signature):
        if not is_hex(message_hash):
            raise ValueError('Invalid message_hash provided')

        return ETHAccount.recoverHash(message_hash, signature=signature)


class Address(object):
    @staticmethod
    def from_hex(address):
        """Helper function that will convert a generic value from hex"""
        if not is_hex(address):
            return address

        return base58.b58encode_check(bytes.fromhex(address))

    @staticmethod
    def to_hex(address):
        """Helper function that will convert a generic value to hex"""
        if is_hex(address):
            return address.lower().replace('0x', '41', 2)

        return base58.b58decode_check(address).hex().upper()

    @staticmethod
    def from_private_key(private_key):
        return PrivateKey(private_key).address


class PrivateKey(object):
    def __init__(self, private_key):
        """Work with private key.
        Getting: PublicKey, PublicToAddress

        Example:::
            PrivateKey("4d1bc37b069b9f2e975c37770b7c87185dc3a10454e3ea024ce1fce8f3eb78bf")
        """
        _private = unhexlify(bytes(private_key, encoding='utf8'))
        self._key = KeyAPI.PrivateKey(_private)
        _length = len(self._key)

        # Key length must not exceed 64 length
        if _length < 64:
            raise ValueError('Key length must not exceed 64 length')

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

        # If bytecode then convert to string
        if is_bytes(to_base58):
            to_base58 = to_base58.decode()

        return AttributeDict({
            'hex': address,
            'base58': to_base58
        })

    def __str__(self):
        return self.private_key

    def __bytes__(self):
        return self._key.to_bytes()
