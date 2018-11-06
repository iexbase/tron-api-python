# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 iEXBase
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from eth_utils import apply_to_return_value

from tronapi.account import Address, GenerateAccount, Account, PrivateKey
from tronapi.exceptions import InvalidTronError, TronError
from tronapi.manager import TronManager
from tronapi.provider import HttpProvider
from tronapi.transactions import TransactionBuilder
from tronapi.trx import Trx
from tronapi.utils.address import is_address
from tronapi.utils.crypto import keccak as tron_keccak
from tronapi.utils.currency import to_sun, from_sun
from tronapi.utils.decorators import deprecated_for
from tronapi.utils.encoding import to_bytes, to_int, to_hex, to_text
from tronapi.utils.hexbytes import HexBytes

DEFAULT_MODULES = {
    'trx': Trx
}


class Tron:
    _default_block = 'latest'
    _default_address = Address(hex=None,
                               base58=None)
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
    def default_address(self) -> Address:
        """Get a TRON Address"""
        return self._default_address

    @default_address.setter
    def default_address(self, address: str) -> None:
        """Sets the address used with all Tron API's.
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

        self._default_address.hex = _hex
        self._default_address.base58 = _base58

    def get_event_result(self, contract_address=None, since=0, event_name=None, block_number=None):
        """Will return all events matching the filters.

        Args:
            contract_address (str): Address to query for events.
            since (int): Filter for events since certain timestamp.
            event_name (str): Name of the event to filter by.
            block_number (str): Specific block number to query

        Examples:
            >>> tron.get_event_result('TQyXdrUaZaw155WrB3F3HAZZ3EeiLVx4V2', 0)

        """

        if not self.manager.event_server:
            raise TronError('No event server configured')

        if not self.isAddress(contract_address):
            raise InvalidTronError('Invalid contract address provided')

        if event_name and not contract_address:
            raise TronError('Usage of event name filtering requires a contract address')

        if block_number and not event_name:
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

        Examples:
            >>> tron.get_event_transaction_id('660028584562b3ae687090f77e989bc7b0bc8b0a8f677524630002c06fd1d57c')

        """

        if not self.manager.event_server:
            raise TronError('No event server configured')

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

    @staticmethod
    def create_account():
        """Create account"""
        return GenerateAccount()

    def generate_address(self):
        """Generates a random private key and address pair

        Warning: Please control risks when using this API.
        To ensure environmental security, please do not invoke APIs
        provided by other or invoke this very API on a public network.

        Returns:
            Value is the corresponding address for the password, encoded in hex.
            Convert it to base58 to use as the address.

        """
        return self.manager.request('/wallet/generateaddress')

    @staticmethod
    def is_valid_provider(provider) -> bool:
        """Check connected provider

        Args:
            provider(HttpProvider): Provider
        """
        return isinstance(provider, HttpProvider)

    @staticmethod
    @deprecated_for("This method has been renamed to keccak")
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

    @property
    def is_connected(self):
        """List of available providers"""
        return self.manager.is_connected()
