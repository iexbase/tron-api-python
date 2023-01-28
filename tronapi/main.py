# -*- coding: utf-8 -*-
# --------------------------------------------------------------------
# Copyright (c) iEXBase. All rights reserved.
# Licensed under the MIT License.
# See License.txt in the project root for license information.
# --------------------------------------------------------------------

"""
    tronapi.main
    ===============

    Connect to the Tron network.

    :copyright: © 2019 by the iEXBase.
    :license: MIT License
"""

from tronapi.common.datastructures import AttributeDict
from urllib.parse import urlencode
from eth_utils import (
    apply_to_return_value,
    to_hex,
    keccak as tron_keccak,
)
from hexbytes import HexBytes
from trx_utils import (
    to_sun,
    from_sun,
    is_integer,
    add_0x_prefix,
    remove_0x_prefix,
    is_address
)

from tronapi.common.abi import map_abi_data


from tronapi.common.account import Address, PrivateKey, Account
from tronapi.common.normalizers import abi_resolver
from tronapi.common.encoding import (
    to_bytes,
    to_int,
    to_text,
    to_json,
    hex_encode_abi_type
)

from tronapi.exceptions import (
    InvalidTronError,
    TronError
)
from tronapi.manager import TronManager
from tronapi import HttpProvider, constants
from tronapi.transactionbuilder import TransactionBuilder
from tronapi.trx import Trx


DEFAULT_MODULES = {
    'trx': Trx
}


class Tron:
    # Providers
    HTTPProvider = HttpProvider

    _default_block = None
    _private_key = None
    _default_address = AttributeDict({})

    # Encoding and Decoding
    toBytes = staticmethod(to_bytes)
    toInt = staticmethod(to_int)
    toHex = staticmethod(to_hex)
    toText = staticmethod(to_text)
    toJSON = staticmethod(to_json)

    # Currency Utility
    toSun = staticmethod(to_sun)
    fromSun = staticmethod(from_sun)

    # Validate address
    isAddress = staticmethod(is_address)

    def __init__(self, **kwargs):
        """Connect to the Tron network.

        Args:
            kwargs (Any): We fill the most necessary parameters
            for working with blockchain Tron

        """

        # We check the obtained nodes, if the necessary parameters
        # are not specified, then we take the default
        kwargs.setdefault('full_node', constants.DEFAULT_NODES['full_node'])
        kwargs.setdefault('solidity_node', constants.DEFAULT_NODES['solidity_node'])
        kwargs.setdefault('event_server', constants.DEFAULT_NODES['event_server'])

        # The node manager allows you to automatically determine the node
        # on the router or manually refer to a specific node.
        # solidity_node, full_node or event_server
        self.manager = TronManager(self, dict(
            full_node=kwargs.get('full_node'),
            solidity_node=kwargs.get('solidity_node'),
            event_server=kwargs.get('event_server')
        ))

        # If the parameter of the private key is not empty,
        # then write to the variable
        if 'private_key' in kwargs:
            self.private_key = kwargs.get('private_key')

        # We check whether the default wallet address is set when
        # defining the class, and then written to the variable
        if 'default_address' in kwargs:
            self.default_address = kwargs.get('default_address')

        # If custom methods are not declared,
        # we take the default from the list
        modules = kwargs.setdefault('modules', DEFAULT_MODULES)
        for module_name, module_class in modules.items():
            module_class.attach(self, module_name)

        self.transaction_builder = TransactionBuilder(self)

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

    def get_event_result(self, **kwargs):
        """Will return all events matching the filters.

        Args:
            kwargs (any): List parameters
        """

        # Check the most necessary parameters
        since_timestamp = kwargs.setdefault('since_timestamp', 0)
        event_name = kwargs.setdefault('event_name', 'Notify')
        block_number = kwargs.setdefault('block_number', '')
        size = kwargs.setdefault('size', 20)
        page = kwargs.setdefault('page', 1)
        only_confirmed = kwargs.setdefault('only_confirmed', None)
        only_unconfirmed = kwargs.setdefault('only_unconfirmed', None)
        previous_last = kwargs.setdefault('previous_last_event_fingerprint', None)
        contract_address = kwargs.setdefault('contract_address', self.default_address.hex)

        if not self.isAddress(contract_address):
            raise InvalidTronError('Invalid contract address provided')

        if event_name and not contract_address:
            raise TronError('Usage of event name filtering requires a contract address')

        if block_number and event_name is None:
            raise TronError('Usage of block number filtering requires an event name')

        if not is_integer(page):
            raise ValueError('Invalid size provided')

        if not is_integer(since_timestamp):
            raise ValueError('Invalid sinceTimestamp provided')

        # If the size exceeds 200, displays an error
        if size > 200:
            raise ValueError('Defaulting to maximum accepted size: 200')

        # We collect all parameters in one array
        route_params = []
        if contract_address:
            route_params.append(contract_address)
        if event_name:
            route_params.append(event_name)
        if block_number:
            route_params.append(block_number)

        route = '/'.join(route_params)

        qs = {
            'since': since_timestamp,
            'page': page,
            'size': size
        }

        if only_confirmed is not None:
            qs.update({'onlyConfirmed': only_confirmed})

        if only_unconfirmed is not None and not only_confirmed:
            qs.update({'onlyUnconfirmed': only_unconfirmed})

        if previous_last is not None:
            qs.update({'previousLastEventFingerprint': previous_last})

        return self.manager.request("/event/contract/{0}?{1}"
                                    .format(route, urlencode(qs)), method='get')

    def get_event_transaction_id(self, tx_id):
        """Will return all events within a transactionID.

        Args:
            tx_id (str): TransactionID to query for events.
        """
        response = self.manager.request('/event/transaction/' + tx_id, method='get')
        return response

    @property
    def address(self) -> Address:
        """Helper object that allows you to convert
        between hex/base58 and private key representations of a TRON address.

        Note:
            If you wish to convert generic data to hexadecimal strings,
            please use the function tron.to_hex.

        """
        return Address()

    @property
    def create_account(self) -> PrivateKey:
        """Create account

        Warning: Please control risks when using this API.
        To ensure environmental security, please do not invoke APIs
        provided by other or invoke this very API on a public network.

        """
        return Account.create()

    @staticmethod
    def is_valid_provider(provider) -> bool:
        """Check connected provider

        Args:
            provider(HttpProvider): Provider
        """
        return isinstance(provider, HttpProvider)

    def solidity_sha3(self, abi_types, values):
        """
            Executes keccak256 exactly as Solidity does.
            Takes list of abi_types as inputs -- `[uint24, int8[], bool]`
            and list of corresponding values  -- `[20, [-1, 5, 0], True]`

            Args:
                abi_types (any): types abi
                values (any): values

            Examples:
                >>> tron = Tron()
                >>> sol = tron.solidity_sha3(['uint8[]'], [[1, 2, 3, 4, 5]])
                >>> assert sol.hex() == '0x5917e5a395fb9b454434de59651d36822a9e29c5ec57474df3e67937b969460c'

        """
        if len(abi_types) != len(values):
            raise ValueError(
                "Length mismatch between provided abi types and values.  Got "
                "{0} types and {1} values.".format(len(abi_types), len(values))
            )

        normalized_values = map_abi_data([abi_resolver()], abi_types, values)

        hex_string = add_0x_prefix(''.join(
            remove_0x_prefix(hex_encode_abi_type(abi_type, value))
            for abi_type, value
            in zip(abi_types, normalized_values)
        ))
        return self.keccak(hexstr=hex_string)

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
                primitive,
                {'text': text, 'hexstr': hexstr}
            )
        )

    def is_connected(self):
        """List of available providers"""
        return self.manager.is_connected()
