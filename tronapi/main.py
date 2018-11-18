# -*- coding: utf-8 -*-
# --------------------------------------------------------------------
# Copyright (c) iEXBase. All rights reserved.
# Licensed under the MIT License.
# See License.txt in the project root for license information.
# --------------------------------------------------------------------

import ecdsa
from eth_utils import apply_to_return_value
from hexbytes import HexBytes

from tronapi.base.account import Account, PrivateKey
from tronapi.base.datastructures import AttributeDict
from tronapi.base.decorators import deprecated_for

from tronapi.exceptions import InvalidTronError, TronError
from tronapi.manager import TronManager
from tronapi import HttpProvider
from tronapi.transactionbuilder import TransactionBuilder
from tronapi.trx import Trx
from tronapi.base.validation import is_address
from tronapi.utils.crypto import keccak as tron_keccak
from tronapi.utils.currency import to_sun, from_sun
from tronapi.utils.encoding import to_bytes, to_int, to_hex, to_text
from tronapi.utils.types import is_integer

DEFAULT_MODULES = {
    'trx': Trx
}


class Tron:
    _default_block = None
    _private_key = None

    # Encoding and Decoding
    toBytes = staticmethod(to_bytes)
    toInt = staticmethod(to_int)
    toHex = staticmethod(to_hex)
    toText = staticmethod(to_text)

    # Currency Utility
    toSun = staticmethod(to_sun)
    fromSun = staticmethod(from_sun)

    # Validate address
    isAddress = staticmethod(is_address)

    def __init__(self, full_node, solidity_node,
                 event_server=None, private_key=None):
        """Connect to the Tron network.

        Args:
            full_node (:obj:`str`): A provider connected to a valid full node
            solidity_node (:obj:`str`): A provider connected to a valid solidity node
            event_server (:obj:`str`, optional): Optional for smart contract events. Expects a valid event server URL
            private_key (str): Optional default private key used when signing transactions

        """

        self._default_address = AttributeDict({})

        # The node manager allows you to automatically determine the node
        # on the router or manually refer to a specific node.
        # solidity_node, full_node or event_server
        self.manager = TronManager(self, dict(
            full_node=full_node,
            solidity_node=solidity_node,
            event_server=event_server
        ))

        if private_key is not None:
            self.private_key = private_key

        for module_name, module_class in DEFAULT_MODULES.items():
            module_class.attach(self, module_name)

        self.transaction = TransactionBuilder(self)

    @property
    def default_block(self):
        return self._default_block

    @default_block.setter
    def default_block(self, block_id):
        """Sets the default block used as a reference for all future calls."""
        if block_id in ('latest', 'earliest', 0):
            self._default_block = block_id
            return

        if not is_integer(block_id) or not block_id:
            raise ValueError('Invalid block ID provided')

        self._default_block = abs(block_id)

    @property
    def providers(self):
        """List providers"""
        return self.manager.providers

    @property
    def private_key(self):
        """Get a private key"""
        return self._private_key

    @private_key.setter
    def private_key(self, value: str) -> None:
        """Set a private key used with the TronAPI instance,
        used for obtaining the address, signing transactions etc...

        Args:
            value (str): Private key
        """
        try:
            private_key = PrivateKey(value)
        except ValueError:
            raise TronError('Invalid private key provided')

        self._private_key = str(private_key).lower()

    @property
    def default_address(self) -> AttributeDict:
        """Get a TRON Address"""
        return self._default_address

    @default_address.setter
    def default_address(self, address: str) -> None:
        """Sets the address used with all Tron API.
        Will not sign any transactions.

        Args:
             address (str) Tron Address

        """

        if not self.isAddress(address):
            raise InvalidTronError('Invalid address provided')

        _hex = self.address.to_hex(address)
        _base58 = self.address.from_hex(address)
        _private_base58 = self.address.from_private_key(self._private_key).base58

        # check the addresses
        if self._private_key and _private_base58 != _base58:
            self._private_key = None

        self._default_address = AttributeDict({
            'hex': _hex,
            'base58': _base58
        })

    def get_event_result(self, contract_address=None, since=0, event_name=None, block_number=None):
        """Will return all events matching the filters.

        Args:
            contract_address (str): Address to query for events.
            since (int): Filter for events since certain timestamp.
            event_name (str): Name of the event to filter by.
            block_number (str): Specific block number to query
        """

        if not self.isAddress(contract_address):
            raise InvalidTronError('Invalid contract address provided')

        if event_name and not contract_address:
            raise TronError('Usage of event name filtering requires a contract address')

        if block_number and event_name is None:
            raise TronError('Usage of block number filtering requires an event name')

        route_params = []

        if contract_address:
            route_params.append(contract_address)

        if event_name:
            route_params.append(event_name)

        if block_number:
            route_params.append(block_number)

        route = '/'.join(route_params)

        return self.manager.request("/event/contract/{0}?since={1}".format(route, since), method='get')

    def get_event_transaction_id(self, tx_id):
        """Will return all events within a transactionID.

        Args:
            tx_id (str): TransactionID to query for events.
        """
        response = self.manager.request('/event/transaction/' + tx_id, method='get')
        return response

    @property
    def address(self):
        """Helper object that allows you to convert
        between hex/base58 and private key representations of a TRON address.

        Note:
            If you wish to convert generic data to hexadecimal strings,
            please use the function tron.to_hex.

        """
        return Account()

    @property
    def create_account(self) -> PrivateKey:
        """Create account

        Warning: Please control risks when using this API.
        To ensure environmental security, please do not invoke APIs
        provided by other or invoke this very API on a public network.

        """
        generate_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        return PrivateKey(generate_key.to_string().hex())

    @staticmethod
    def is_valid_provider(provider) -> bool:
        """Check connected provider

        Args:
            provider(HttpProvider): Provider
        """
        return isinstance(provider, HttpProvider)

    @staticmethod
    @deprecated_for("keccak")
    @apply_to_return_value(HexBytes)
    def sha3(primitive=None, text=None, hexstr=None):
        """Returns the Keccak SHA256 of the given value.
        Text is encoded to UTF-8 before computing the hash, just like Solidity.
        Any of the following are valid and equivalent:
        """
        return Tron.keccak(primitive, text, hexstr)

    @staticmethod
    @apply_to_return_value(HexBytes)
    def keccak(primitive=None, text=None, hexstr=None):
        if isinstance(primitive, (bytes, int, type(None))):
            input_bytes = to_bytes(primitive, hexstr=hexstr, text=text)
            return tron_keccak(input_bytes)

        raise TypeError(
            "You called keccak with first arg %r and keywords %r. You must call it with one of "
            "these approaches: keccak(text='txt'), keccak(hexstr='0x747874'), "
            "keccak(b'\\x74\\x78\\x74'), or keccak(0x747874)." % (
                primitive, {'text': text, 'hexstr': hexstr}
            )
        )

    def is_connected(self):
        """List of available providers"""
        return self.manager.is_connected()
