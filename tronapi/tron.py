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


import math

from eth_utils import apply_to_return_value

from tronapi.account import Address, GenerateAccount, Account, PrivateKey
from tronapi.event import Event
from tronapi.exceptions import InvalidTronError, TronError
from tronapi.manager import TronManager
from tronapi.provider import HttpProvider
from tronapi.transactions import TransactionBuilder
from tronapi.utils.address import is_address
from tronapi.utils.blocks import select_method_for_block
from tronapi.utils.crypto import keccak as tron_keccak
from tronapi.utils.currency import to_sun, from_sun
from tronapi.utils.decorators import deprecated_for
from tronapi.utils.encoding import to_bytes, to_int, to_hex, to_text
from tronapi.utils.hexbytes import HexBytes
from tronapi.utils.types import is_integer, is_object


class Tron(object):
    # Encoding and Decoding
    toBytes = staticmethod(to_bytes)
    toInt = staticmethod(to_int)
    toHex = staticmethod(to_hex)
    toText = staticmethod(to_text)

    # Currency Utility
    toSun = staticmethod(to_sun)
    fromSun = staticmethod(from_sun)

    # Address Utility
    isAddress = staticmethod(is_address)

    def __init__(self, full_node, solidity_node,
                 event_server=None, private_key=None):
        """Connect to the Tron network.

        Parameters:
            full_node (:obj:`str`): A provider connected to a valid full node
            solidity_node (:obj:`str`): A provider connected to a valid solidity node
            event_server (:obj:`str`, optional): Optional for smart contract events. Expects a valid event server URL
            private_key (str): Optional default private key used when signing transactions
        """

        self.manager = TronManager(self, dict(
            full_node=full_node,
            solidity_node=solidity_node
        ))

        self._default_block = None
        self._private_key = private_key
        self.default_address = Address(base58=None, hex=None)

        self.events = Event(self, event_server)
        self.transaction = TransactionBuilder(self)

    @property
    def providers(self):
        is_nodes = self.manager.is_connected()
        is_nodes.update({'event': self.events.is_event_connected()})

        return is_nodes

    def set_private_key(self, private_key) -> None:
        """Set a private key used with the TronAPI instance,
        used for obtaining the address, signing transactions etc...

        Args:
            private_key (str): Private key

        Warning:
            Do not use this with any web/user facing TronAPI instances.
            This will leak the private key.
        """

        try:
            check = PrivateKey(private_key).public_key
        except ValueError:
            raise TronError('Invalid private key provided')

        self._private_key = str(private_key).lower()

    def set_address(self, address):
        """Sets the address used with all Tron API's. Will not sign any transactions.

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

        self.default_address = Address(hex=_hex, base58=_base58)

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

    def get_current_block(self):
        """Query the latest block

        Returns:
            Latest block on full node
        """
        return self.manager.request(url='/wallet/getnowblock')

    def get_block(self, block=None):
        """Get block details using HashString or blockNumber

        Args:
            block (int|str): Number or Hash Block

        """

        if block is None:
            raise ValueError('No block identifier provided')

        if block == 'latest':
            return self.get_current_block()
        elif block == 'earliest':
            return self.get_block(0)

        method = select_method_for_block(
            block,
            if_hash={'url': '/wallet/getblockbyid', 'field': 'value'},
            if_number={'url': '/wallet/getblockbynum', 'field': 'num'},
        )

        response = self.manager.request(method['url'], {
            method['field']: block
        })

        if len(response) == 0:
            raise ValueError('Block not found')

        return response

    def get_block_transaction_count(self, block=None):
        """Total number of transactions in a block

        Args:
            block (int | str): Number or Hash Block

        """
        transaction = self.get_block(block)

        if 'transactions' not in transaction:
            raise TronError('Parameter "transactions" not found')

        if transaction is None:
            return 0

        return len(transaction)

    def get_transaction_from_block(self, block=None, index=0):
        """Get transaction details from Block

        Args:
            block (int|str): Number or Hash Block
            index (int) Position

        """
        if not is_integer(index) or index < 0:
            raise InvalidTronError('Invalid transaction index provided')

        transactions = self.get_block(block).get('transactions')

        if not transactions or len(transactions) < index:
            raise TronError('Transaction not found in block')

        return transactions[index]

    def get_transaction(self, transaction_id):
        """Query transaction based on id

        Args:
            transaction_id (str): transaction id

        """

        response = self.manager.request('/wallet/gettransactionbyid', {
            'value': transaction_id
        })

        if not response:
            raise TronError('Transaction not found')

        return response

    def get_account_resource(self, address=None):
        """Query the resource information of the account

        Args:
            address (str): Address

        Results:
            Resource information of the account

        """

        if address is None:
            address = self.default_address.hex

        if not self.isAddress(address):
            raise InvalidTronError('Invalid address provided')

        return self.manager.request('/wallet/getaccountresource', {
            'address': self.address.to_hex(address)
        })

    def get_account(self, address=None):
        """Query information about an account

        Args:
            address (str): Address

        """

        if address is None:
            address = self.default_address.hex

        if not self.isAddress(address):
            raise InvalidTronError('Invalid address provided')

        return self.manager.request('/walletsolidity/getaccount', {
            'address': self.address.to_hex(address)
        })

    def get_balance(self, address=None, is_float=False):
        """Getting a balance

        Args:
            address (str): Address
            is_float (bool): Convert to float format

        """
        response = self.get_account(address)

        if 'balance' not in response:
            return 0

        if is_float:
            return self.fromSun(response['balance'])

        return response['balance']

    def get_transactions_related(self, address, direction='all', limit=30, offset=0):
        """Getting data in the "from", "to" and "all" directions

        Args:
            address (str): Address
            direction (str): Type direction
            address (str): address
            limit (int): number of transactions expected to be returned
            offset (int): index of the starting transaction

        """

        if direction not in ['from', 'to', 'all']:
            raise InvalidTronError('Invalid direction provided: Expected "to", "from" or "all"')

        if direction == 'all':
            from_direction = {'from': self.get_transactions_related(address, 'from', limit, offset)}
            to_direction = {'to': self.get_transactions_related(address, 'to', limit, offset)}

            callback = from_direction
            callback.update(to_direction)
            return callback

        if address is None:
            address = self.default_address.hex

        if not self.isAddress(address):
            raise InvalidTronError('Invalid address provided')

        if not isinstance(limit, int) or limit < 0 or (offset and limit < 1):
            raise InvalidTronError('Invalid limit provided')

        if not isinstance(offset, int) or offset < 0:
            raise InvalidTronError('Invalid offset provided')

        path = '/walletextension/gettransactions{0}this'.format(direction)
        response = self.manager.request(path, {
            'account': {
                'address': self.address.to_hex(address)
            },
            'limit': limit,
            'offset': offset
        })

        # response.update({'direction': direction})
        return response

    def get_transactions_to_address(self, address=None, limit=30, offset=0):
        """Query the list of transactions received by an address

        Args:
            address (str): address
            limit (int): number of transactions expected to be returned
            offset (int): index of the starting transaction

        Returns:
            Transactions list

        """
        return self.get_transactions_related(address, 'to', limit, offset)

    def get_transactions_from_address(self, address=None, limit=30, offset=0):
        """Query the list of transactions sent by an address

        Args:
            address (str): address
            limit (int): number of transactions expected to be returned
            offset (int): index of the starting transaction

        Returns:
            Transactions list

        """
        return self.get_transactions_related(address, 'from', limit, offset)

    def get_transaction_info(self, tx_id):
        """Query transaction fee based on id

        Args:
            tx_id (str): Transaction Id

        Returns:
            Transaction fee，block height and block creation time

        """
        response = self.manager.request('/walletsolidity/gettransactioninfobyid', {
            'value': tx_id
        })

        return response

    def get_band_width(self, address=None):
        """Query bandwidth information.

        Args:
            address (str): address

        Returns:
            Bandwidth information for the account.
            If a field doesn't appear, then the corresponding value is 0.
            {
                "freeNetUsed": 557,
                "freeNetLimit": 5000,
                "NetUsed": 353,
                "NetLimit": 5239157853,
                "TotalNetLimit": 43200000000,
                "TotalNetWeight": 41228
            }

        """

        if address is None:
            address = self.default_address.hex

        if not self.isAddress(address):
            raise InvalidTronError('Invalid address provided')

        return self.manager.request('/wallet/getaccountnet', {
            'address': self.address.to_hex(address)
        })

    def get_transaction_count(self):
        """Count all transactions on the network
        Note: Possible delays

        Returns:
            Total number of transactions.

        """
        response = self.manager.request('/wallet/totaltransaction')
        return response.get('num')

    def send(self, *args):
        """Send funds to the Tron account (option 2)

        Returns:
            Returns the details of the transaction being sent.
            [result = 1] - Successfully sent

            """
        return self.send_transaction(*args)

    def send_trx(self, *args):
        """Send funds to the Tron account (option 3)

        Returns:
            Returns the details of the transaction being sent.
             [result = 1] - Successfully sent

        """
        return self.send_transaction(*args)

    def send_transaction(self, to, amount, message=None,
                         owner_address=None):
        """Send an asset to another account.

        Parameters:
            to (str): Recipient
            amount (float): Amount to transfer
            message (str, optional): Message
            owner_address (str, optional): the source account for the transfer
                if not ``default_address``

        """

        if owner_address is None:
            owner_address = self.default_address.hex

        if message is not None and not isinstance(message, str):
            raise InvalidTronError('Invalid Message')

        tx = self.transaction.send_transaction(to, amount, owner_address)
        sign = self.sign(tx, message)
        result = self.broadcast(sign)

        return result

    def send_token(self, to, amount, token_id=None, owner_address=None):

        if owner_address is None:
            owner_address = self.default_address.hex

        tx = self.transaction.send_token(to, amount, token_id, owner_address)
        sign = self.sign(tx)
        result = self.broadcast(sign)

        return result

    def freeze_balance(self, amount=0, duration=3, resource='BANDWIDTH', account=None):
        """
        Freezes an amount of TRX.
        Will give bandwidth OR Energy and TRON Power(voting rights)
        to the owner of the frozen tokens.

        Args:
            amount (int): number of frozen trx
            duration (int): duration in days to be frozen
            resource (str): type of resource, must be either "ENERGY" or "BANDWIDTH"
            account (str): address that is freezing trx account

        """

        if account is None:
            account = self.default_address.hex

        transaction = self.transaction.freeze_balance(amount, duration, resource, account)
        sign = self.sign(transaction)
        response = self.broadcast(sign)

        return response

    def unfreeze_balance(self, resource='BANDWIDTH', account=None):
        """
        Unfreeze TRX that has passed the minimum freeze duration.
        Unfreezing will remove bandwidth and TRON Power.

        Args:
            resource (str): type of resource, must be either "ENERGY" or "BANDWIDTH"
            account (str): address that is freezing trx account

        """

        if account is None:
            account = self.default_address.hex

        transaction = self.transaction.unfreeze_balance(resource, account)
        sign = self.sign(transaction)
        response = self.broadcast(sign)

        return response

    def sign(self, transaction, message=None):
        """Sign the transaction, the api has the risk of leaking the private key,
        please make sure to call the api in a secure environment

        Args:
            transaction (object): transaction details
            message (str): Message

        Returns:
            Signed Transaction contract data

        """

        if 'signature' in transaction:
            raise TronError('Transaction is already signed')

        if message is not None:
            transaction['raw_data']['data'] = self.toHex(text=message)

        address = self.address.from_private_key(self._private_key).hex.lower()
        owner_address = transaction['raw_data']['contract'][0]['parameter']['value']['owner_address']

        if address != owner_address:
            raise ValueError('Private key does not match address in transaction')

        return self.manager.request('/wallet/gettransactionsign', {
            'transaction': transaction,
            'privateKey': self._private_key
        })

    def broadcast(self, signed_transaction):
        """Broadcast the signed transaction

        Args:
            signed_transaction (object): signed transaction contract data

        Returns:
            broadcast success or failure

        """
        if not is_object(signed_transaction):
            raise InvalidTronError('Invalid transaction provided')

        if 'signature' not in signed_transaction:
            raise TronError('Transaction is not signed')

        result = self.manager.request('/wallet/broadcasttransaction', signed_transaction)
        result.update(signed_transaction)

        return result

    def update_account(self, account_name, address=None):
        """Modify account name

        Note: Username is allowed to edit only once.

        Args:
            account_name (str): name of the account
            address (str): address

        Returns:
            modified Transaction Object

        """
        if address is None:
            address = self.default_address.hex

        transaction = self.transaction.update_account(account_name, address)
        sign = self.sign(transaction)
        response = self.broadcast(sign)

        return response

    def register_account(self, address, new_account_address):
        """Create an account.
        Uses an already activated account to create a new account

        Args:
            address (str): address
            new_account_address (str): address of the new account

        Returns:
            Create account Transaction raw data

        """
        return self.manager.request('/wallet/createaccount', {
            'owner_address': self.address.to_hex(address),
            'account_address': self.address.to_hex(new_account_address)
        }, 'post')

    @staticmethod
    def create_account():
        """Create account"""
        return GenerateAccount()

    def apply_for_super_representative(self, address, url):
        """Apply to become a super representative

        Note: Applied to become a super representative. Cost 9999 TRX.

        Args:
            address (str): address
            url (str): official website address

        """

        return self.manager.request('/wallet/createwitness', {
            'owner_address': self.address.to_hex(address),
            'url': self.toHex(text=url)
        }, 'post')

    def list_nodes(self):
        """List the nodes which the api fullnode is connecting on the network

        Returns:
            List of nodes

        """
        response = self.manager.request('/wallet/listnodes')
        callback = map(lambda x: {
            'address': '{}:{}'.format(self.toText(x['address']['host']), str(x['address']['port']))
        }, response['nodes'])

        return list(callback)

    def get_tokens_issued_by_address(self, address):
        """List the tokens issued by an account.

        Args:
            address (str): address

        Returns:
            The token issued by the account.
            An account can issue only one token.

        """

        if not self.isAddress(address):
            raise InvalidTronError('Invalid address provided')

        address = self.address.to_hex(address)

        return self.manager.request('/wallet/getassetissuebyaccount', {
            'address': address
        })

    def get_token_from_id(self, token_id: str):
        """Query token by name.

        Args:
            token_id (str): The name of the token

        """
        if not isinstance(token_id, str) or not len(token_id):
            raise InvalidTronError('Invalid token ID provided')

        return self.manager.request('/wallet/getassetissuebyname', {
            'value': self.toHex(text=token_id)
        })

    def get_block_range(self, start, end):
        """Query a range of blocks by block height

        Args:
            start (int): starting block height, including this block
            end (int): ending block height, excluding that block

        """
        if not is_integer(start) or start < 0:
            raise InvalidTronError('Invalid start of range provided')

        if not is_integer(end) or end <= start:
            raise InvalidTronError('Invalid end of range provided')

        response = self.manager.request('/wallet/getblockbylimitnext', {
            'startNum': int(start),
            'endNum': int(end) + 1
        }, 'post')

        return response.get('block')

    def get_latest_blocks(self, num=1):
        """Query the latest blocks

        Args:
            num (int): the number of blocks to query

        """
        if not is_integer(num) or num <= 0:
            raise InvalidTronError('Invalid limit provided')

        response = self.manager.request('/wallet/getblockbylatestnum', {
            'num': num
        })

        return response.get('block')

    def list_super_representatives(self):
        """Query the list of Super Representatives"""
        response = self.manager.request('/wallet/listwitnesses')
        return response.get('witnesses')

    def list_tokens(self, limit=0, offset=0):
        """Query the list of Tokens with pagination

        Args:
            limit (int): index of the starting Token
            offset (int): number of Tokens expected to be returned

        Returns:
            List of Tokens

        """
        if not is_integer(limit) or (limit and offset < 1):
            raise InvalidTronError('Invalid limit provided')

        if not is_integer(offset) or offset < 0:
            raise InvalidTronError('Invalid offset provided')

        if not limit:
            return self.manager.request('/wallet/getassetissuelist').get('assetIssue')

        return self.manager.request('/wallet/getpaginatedassetissuelist', {
            'limit': int(limit),
            'offset': int(offset)
        })

    def time_until_next_vote_cycle(self):
        """Get the time of the next Super Representative vote

        Returns:
            Number of milliseconds until the next voting time.

        """
        num = self.manager.request('/wallet/getnextmaintenancetime').get('num')

        if num == -1:
            raise Exception('Failed to get time until next vote cycle')

        return math.floor(num / 1000)

    def get_contract(self, contract_address):
        """Queries a contract's information from the blockchain.

        Args:
            contract_address (str): contract address

        Returns:
            SmartContract object.

        """

        if not self.isAddress(contract_address):
            raise InvalidTronError('Invalid contract address provided')

        return self.manager.request('/wallet/getcontract', {
            'value': self.address.to_hex(contract_address)
        })

    def validate_address(self, address, _is_hex=False):
        """Validate address

        Args:
            address (str): The address, should be in base58checksum
            _is_hex (bool): hexString or base64 format

        """
        if _is_hex:
            address = self.address.to_hex(address)

        return self.manager.request('/wallet/validateaddress', {
            'address': address
        })

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

    def get_chain_parameters(self):
        """Getting chain parameters"""
        return self.manager.request('/wallet/getchainparameters')

    def get_exchange_by_id(self, exchange_id):
        """Find exchange by id

        Args:
             exchange_id (str): ID Exchange
        """

        if not isinstance(exchange_id, int) or exchange_id < 0:
            raise InvalidTronError('Invalid exchangeID provided')

        return self.manager.request('/wallet/getexchangebyid', {
            'id': exchange_id
        })

    def get_list_exchangers(self):
        """Get list exchangers"""
        return self.manager.request('/wallet/listexchanges')

    def get_proposal(self, proposal_id):
        """Query proposal based on id

        Args:
            proposal_id (int): ID

        """
        if not isinstance(proposal_id, int) or proposal_id < 0:
            raise InvalidTronError('Invalid proposalID provided')

        return self.manager.request('/wallet/getproposalbyid', {
            'id': int(proposal_id)
        })

    def list_proposals(self):
        """Query all proposals

        Returns:
            Proposal list information

        """
        return self.manager.request('/wallet/listproposals')

    def proposal_approve(self, owner_address, proposal_id, is_add_approval=True):
        """Proposal approval

        Args:
            owner_address (str): Approve address
            proposal_id (int): proposal id
            is_add_approval (bool): Approved

        Returns:
             Approval of the proposed transaction

        """
        if not self.isAddress(owner_address):
            raise InvalidTronError('Invalid address provided')

        if not isinstance(proposal_id, int) or proposal_id < 0:
            raise InvalidTronError('Invalid proposalID provided')

        return self.manager.request('/wallet/proposalapprove', {
            'owner_address': self.address.to_hex(owner_address),
            'proposal_id': proposal_id,
            'is_add_approval': is_add_approval
        })

    def proposal_delete(self, owner_address, proposal_id):
        """Delete proposal

        Args:
            owner_address (str): delete the person's address
            proposal_id (int): proposal id

        Results:
            Delete the proposal's transaction

        """
        if not self.isAddress(owner_address):
            raise InvalidTronError('Invalid address provided')

        if not isinstance(proposal_id, int) or proposal_id < 0:
            raise InvalidTronError('Invalid proposalID provided')

        return self.manager.request('/wallet/proposaldelete', {
            'owner_address': self.address.to_hex(owner_address),
            'proposal_id': proposal_id
        })

    def exchange_transaction(self, owner_address, exchange_id,
                             token_id, quant, expected):
        """ Exchanges a transaction.

        Args:
            owner_address (str):  Address of the creator of the transaction pair
            exchange_id (str): transaction pair id
            token_id (str): The id of the sold token
            quant (int): the number of tokens sold
            expected (int): the number of tokens expected to be bought

        """
        if not self.isAddress(owner_address):
            raise InvalidTronError('Invalid address provided')

        if not isinstance(token_id, str) or len(token_id):
            raise InvalidTronError('Invalid token ID provided')

        if not isinstance(quant, int) or quant <= 0:
            raise InvalidTronError('Invalid quantity provided')

        if not isinstance(expected, int) or quant < 0:
            raise InvalidTronError('Invalid expected provided')

        return self.manager.request('/wallet/exchangetransaction', {
            'owner_address': self.address.to_hex(owner_address),
            'exchange_id': exchange_id,
            'token_id': token_id,
            'quant': quant,
            'expected': expected
        })

    def list_exchanges_paginated(self, limit=10, offset=0):
        """Paged query transaction pair list

        Args:
            limit (int): number of trading pairs  expected to be returned.
            offset (int): index of the starting trading pair

        """
        return self.manager.request('/wallet/listexchangespaginated', {
            'limit': limit,
            'offset': offset
        })

    def exchange_create(self, owner_address, first_token_id, second_token_id,
                        first_token_balance, second_token_balance):
        """Create a transaction pair

        Args:
            owner_address (str):
            first_token_id (str): the id of the first token
            second_token_id (str): the id of the second token
            first_token_balance (int): balance of the first token
            second_token_balance (int): balance of the second token

        """
        if not self.isAddress(owner_address):
            raise InvalidTronError('Invalid address provided')

        if isinstance(first_token_id, str) or len(first_token_id) or \
                not isinstance(second_token_id, str) or len(second_token_id):
            raise InvalidTronError('Invalid token ID provided')

        if not isinstance(first_token_balance, int) or first_token_balance <= 0 or \
                not isinstance(second_token_balance, int) or second_token_balance <= 0:
            raise InvalidTronError('Invalid amount provided')

        return self.manager.request('/wallet/exchangecreate', {
            'owner_address': self.address.to_hex(owner_address),
            'first_token_id': first_token_id,
            'first_token_balance': first_token_balance,
            'second_token_id': second_token_id,
            'second_token_balance': second_token_balance
        }, 'post')

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
    @deprecated_for("This method has been renamed to keccak")
    @apply_to_return_value(HexBytes)
    def sha3(primitive=None, text=None, hexstr=None):
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
