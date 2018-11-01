# -*- coding: utf-8 -*-

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

import binascii
from _sha256 import sha256
import base58
import math

from Crypto.Hash import keccak

from tronapi import utils
from tronapi.account import Address, GenerateAccount, Account, PrivateKey
from tronapi.event import Event
from tronapi.exceptions import InvalidTronError, TronError
from tronapi.provider import HttpProvider
from tronapi.transactions import TransactionBuilder


class Tron(object):
    def __init__(self,
                 full_node,
                 solidity_node,
                 event_server=None,
                 private_key=None):
        """Connect to the Tron network.

        Parameters:
            full_node (:obj:`str`): A provider connected to a valid full node
            solidity_node (:obj:`str`): A provider connected to a valid solidity node
            event_server (:obj:`str`, optional): Optional for smart contract events. Expects a valid event server URL
            private_key (str): Optional default private key used when signing transactions

        The idea is to have a class that allows to do this:

        .. code-block:: python
        >>> from tronapi.tron import Tron
        >>>
        >>> full_node = HttpProvider('https://api.trongrid.io')
        >>> solidity_node = HttpProvider('https://api.trongrid.io')
        >>> event_server = 'https://api.trongrid.io'
        >>>
        >>> tron = Tron()
        >>> print(tron.get_current_block())

         This class also deals with edits, votes and reading content.
        """

        # check received nodes
        if utils.is_string(full_node):
            full_node = HttpProvider(full_node)
        if utils.is_string(solidity_node):
            solidity_node = HttpProvider(solidity_node)

        # node setup
        self.__set_full_node(full_node)
        self.__set_solidity_node(solidity_node)

        self._default_block = None
        self._private_key = private_key
        self.default_address = Address(base58=None, hex=None)

        self.events = Event(self, event_server)
        self.transaction = TransactionBuilder(self)

    def set_private_key(self, private_key) -> None:
        """Set a private key used with the TronAPI instance,
        used for obtaining the address, signing transactions etc...

        Args:
            private_key (str): Private key

        Example:
            >>> tron.set_private_key('da146...f0d0')

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

            Example:
                >>> tron.set_address('TSkTw9Hd3oaJULL3er1UNfzASkunE9yA8f')
        """

        if not self.is_address(address):
            raise InvalidTronError('Invalid address provided')

        _hex = self.address.to_hex(address)
        _base58 = self.address.from_hex(address)
        _private_base58 = self.address.from_private_key(self._private_key)

        # check the addresses
        if self._private_key and _private_base58 != _base58:
            self._private_key = None

        self.default_address = Address(hex=_hex, base58=_base58)

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

        if not utils.is_numeric(block_id) or not block_id:
            raise ValueError('Invalid block ID provided')

        self._default_block = abs(block_id)

    def get_current_block(self):
        """Query the latest block

        Returns:
            Latest block on full node
        """
        return self.full_node.request('/wallet/getnowblock', {}, 'post')

    def get_block(self, block=None):
        """Get block details using HashString or blockNumber

        Args:
            block (int|str): Number or Hash Block

        """
        if block is None:
            block = self.default_block

        if block == 'earliest':
            block = 0

        if block == 'latest':
            return self.get_current_block()

        if math.isnan(block) and utils.is_hex(block):
            return self.get_block_by_hash(block)

        return self.get_block_by_number(int(block))

    def get_block_by_hash(self, hash_block):
        """Query block by ID

        Args:
            hash_block (str): Block ID

        Returns:
            Block Object

        """
        return self.full_node.request('/wallet/getblockbyid', {
            'value': hash_block
        }, 'post')

    def get_block_by_number(self, block_id):
        """Query block by height

        Args:
            block_id (int): height of the block

        Returns:
            Block object

        """
        if not utils.is_numeric(block_id) or block_id < 0:
            raise InvalidTronError('Invalid block number provided')

        return self.full_node.request('/wallet/getblockbynum', {
            'num': int(block_id)
        }, 'post')

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
        if not utils.is_numeric(index) or index < 0:
            raise InvalidTronError('Invalid transaction index provided')

        transactions = self.get_block(block)['transactions']

        if not transactions or len(transactions) < index:
            raise TronError('Transaction not found in block')

        return transactions[index]

    def get_transaction(self, transaction_id):
        """Query transaction based on id

        Args:
            transaction_id (str): transaction id

        """
        response = self.full_node.request('/wallet/gettransactionbyid', {
            'value': transaction_id
        }, 'post')

        # if not response:
        #     raise TronError('Transaction not found')

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

        if not self.is_address(address):
            raise InvalidTronError('Invalid address provided')

        return self.full_node.request('/wallet/getaccountresource', {
            'address': self.address.to_hex(address)
        })

    def get_account(self, address=None):
        """Query information about an account

        Args:
            address (str): Address

        """

        if address is None:
            address = self.default_address.hex

        if not self.is_address(address):
            raise InvalidTronError('Invalid address provided')

        return self.solidity_node.request('/walletsolidity/getaccount', {
            'address': self.address.to_hex(address)
        }, 'post')

    def get_balance(self, address=None, from_sun=False):
        """Getting a balance

        Args:
            address (str): Address
            from_sun (bool): Convert to float format

        """
        response = self.get_account(address)

        if 'balance' not in response:
            return 0

        if from_sun:
            return self.from_sun(response['balance'])

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

        if not self.is_address(address):
            raise InvalidTronError('Invalid address provided')

        if not isinstance(limit, int) or limit < 0 or (offset and limit < 1):
            raise InvalidTronError('Invalid limit provided')

        if not isinstance(offset, int) or offset < 0:
            raise InvalidTronError('Invalid offset provided')

        response = self.solidity_node.request('/walletextension/gettransactions{0}this'.format(direction), {
            'account': {
                'address': self.address.to_hex(address)
            },
            'limit': limit,
            'offset': offset
        }, 'post')

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
        response = self.solidity_node.request('/walletsolidity/gettransactioninfobyid', {
            'value': tx_id
        }, 'post')

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

        if not self.is_address(address):
            raise InvalidTronError('Invalid address provided')

        return self.full_node.request('/wallet/getaccountnet', {
            'address': self.address.to_hex(address)
        }, 'post')

    def get_transaction_count(self):
        """Count all transactions on the network

        Note: Possible delays

        Examples:
            >>> tron.get_transaction_count()

        Returns:
            Total number of transactions.

        """
        response = self.full_node.request('/wallet/totaltransaction')

        return response['num']

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
        if not self.is_address(to):
            raise InvalidTronError('Invalid address provided')

        if not isinstance(amount, float) or amount <= 0:
            raise InvalidTronError('Invalid amount provided')

        if owner_address is None:
            owner_address = self.default_address.hex

        if message is not None and not isinstance(message, str):
            raise InvalidTronError('Invalid Message')

        tx = self.transaction.send_trx(to, amount, owner_address)
        sign = self.sign(tx, message)
        result = self.broadcast(sign)

        return result

    def send_token(self, to, amount, token_id=None, owner_address=None):

        if not self.is_address(to):
            raise InvalidTronError('Invalid recipient provided')

        if not isinstance(amount, float) or amount <= 0:
            raise InvalidTronError('Invalid amount provided')

        if not utils.is_string(token_id):
            raise InvalidTronError('Invalid token ID provided')

        if owner_address is None:
            owner_address = self.default_address.hex

        tx = self.transaction.send_token(to, amount, token_id, owner_address)
        sign = self.sign(tx)
        result = self.broadcast(sign)

        return result

    def sign(self, transaction, message=None):
        """Sign the transaction, the api has the risk of leaking the private key,
        please make sure to call the api in a secure environment

        Args:
            transaction (object): transaction details
            message (str): Message

        Returns:
            Signed Transaction contract data

        """
        if not self._private_key:
            raise TronError('Missing private key')

        if 'signature' in transaction:
            raise TronError('Transaction is already signed')

        if message is not None:
            transaction['raw_data']['data'] = self.string_utf8_to_hex(message)

        return self.full_node.request('/wallet/gettransactionsign', {
            'transaction': transaction,
            'privateKey': self._private_key
        }, 'post')

    def broadcast(self, signed_transaction):
        """Broadcast the signed transaction

        Args:
            signed_transaction (object): signed transaction contract data

        Returns:
            broadcast success or failure

        """
        if not utils.is_object(signed_transaction):
            raise InvalidTronError('Invalid transaction provided')

        if 'signature' not in signed_transaction:
            raise TronError('Transaction is not signed')

        result = self.full_node.request(
            '/wallet/broadcasttransaction',
            signed_transaction,
            'post')
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

        if not self.is_address(address):
            raise InvalidTronError('Invalid address provided')

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
        return self.full_node.request('/wallet/createaccount', {
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

        return self.full_node.request('/wallet/createwitness', {
            'owner_address': self.address.to_hex(address),
            'url': self.string_utf8_to_hex(url)
        }, 'post')

    def list_nodes(self):
        """List the nodes which the api fullnode is connecting on the network

        Returns:
            List of nodes

        """
        response = self.full_node.request('/wallet/listnodes')
        callback = map(lambda x: {
            'address': '{}:{}'.format(self.to_utf8(x['address']['host']), str(x['address']['port']))
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

        if not self.is_address(address):
            raise InvalidTronError('Invalid address provided')

        address = self.address.to_hex(address)

        return self.full_node.request('/wallet/getassetissuebyaccount', {
            'address': address
        }, 'post')

    def get_token_from_id(self, token_id):
        """Query token by name.

        Args:
            token_id (str): The name of the token

        """
        if isinstance(token_id, str) or not len(token_id):
            raise InvalidTronError('Invalid token ID provided')

        return self.full_node.request('/wallet/getassetissuebyname', {
            'value': self.from_utf8(token_id)
        }, 'post')

    def get_block_range(self, start, end):
        """Query a range of blocks by block height

        Args:
            start (int): starting block height, including this block
            end (int): ending block height, excluding that block

        Returns:
            A list of Block Objects

        """
        if not utils.is_numeric(start) or start < 0:
            raise InvalidTronError('Invalid start of range provided')

        if not utils.is_numeric(end) or end <= start:
            raise InvalidTronError('Invalid end of range provided')

        response = self.full_node.request('/wallet/getblockbylimitnext', {
            'startNum': int(start),
            'endNum': int(end) + 1
        }, 'post')

        return response['block']

    def get_latest_blocks(self, limit=1):
        """Query the latest blocks

        Args:
            limit (int): the number of blocks to query

        Returns:
            A list of Block Objects

        """
        if not utils.is_numeric(limit) or limit <= 0:
            raise InvalidTronError('Invalid limit provided')

        response = self.full_node.request('/wallet/getblockbylatestnum', {
            'limit': limit
        }, 'post')

        return response['block']

    def list_super_representatives(self):
        """Query the list of Super Representatives

        Examples:
            >>> tron.list_super_representatives()

        Returns:
            List of all Super Representatives

        """
        response = self.full_node.request('/wallet/listwitnesses', {}, 'post')
        return response['witnesses']

    def list_tokens(self, limit=0, offset=0):
        """Query the list of Tokens with pagination

        Args:
            limit (int): index of the starting Token
            offset (int): number of Tokens expected to be returned

        Returns:
            List of Tokens

        """
        if not utils.is_numeric(limit) or (limit and offset < 1):
            raise InvalidTronError('Invalid limit provided')

        if not utils.is_numeric(offset) or offset < 0:
            raise InvalidTronError('Invalid offset provided')

        if not limit:
            return self.full_node.request('/wallet/getassetissuelist')['assetIssue']

        return self.full_node.request('/wallet/getpaginatedassetissuelist', {
            'limit': int(limit),
            'offset': int(offset)
        }, 'post')

    def time_until_next_vote_cycle(self):
        """Get the time of the next Super Representative vote

        Returns:
            Number of milliseconds until the next voting time.

        """
        num = self.full_node.request('/wallet/getnextmaintenancetime')['num']

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

        if not self.is_address(contract_address):
            raise InvalidTronError('Invalid contract address provided')

        contract_address = self.address.to_hex(contract_address)

        return self.full_node.request('/wallet/getcontract', {
            'value': contract_address
        }, 'post')

    def validate_address(self, address, is_hex=False):
        """Validate address

        Args:
            address (str): The address, should be in base58checksum
            is_hex (bool): hexString or base64 format

        """
        if is_hex:
            address = self.address.to_hex(address)

        return self.full_node.request('/wallet/validateaddress', {
            'address': address
        }, 'post')

    def generate_address(self):
        """Generates a random private key and address pair

        Warning: Please control risks when using this API.
        To ensure environmental security, please do not invoke APIs
        provided by other or invoke this very API on a public network.

        Returns:
            Value is the corresponding address for the password, encoded in hex.
            Convert it to base58 to use as the address.

        """
        response = self.full_node.request('/wallet/generateaddress', {}, 'post')
        return response

    def get_chain_parameters(self):
        """Getting chain parameters"""
        return self.full_node.request('/wallet/getchainparameters', {}, 'post')

    def get_exchange_by_id(self, exchange_id):
        """Find exchange by id

        Args:
             exchange_id (str): ID Exchange
        """

        if not isinstance(exchange_id, int) or exchange_id < 0:
            raise InvalidTronError('Invalid exchangeID provided')

        return self.full_node.request('/wallet/getexchangebyid', {
            'id': exchange_id
        }, 'post')

    def get_list_exchangers(self):
        """Get list exchangers"""
        return self.full_node.request('/wallet/listexchanges', {}, 'post')

    def get_proposal(self, proposal_id):
        """Query proposal based on id

        Args:
            proposal_id (int): ID

        """
        if not isinstance(proposal_id, int) or proposal_id < 0:
            raise InvalidTronError('Invalid proposalID provided')

        return self.full_node.request('/wallet/getproposalbyid', {
            'id': int(proposal_id)
        }, 'post')

    def list_proposals(self):
        """Query all proposals

        Returns:
            Proposal list information

        """
        return self.full_node.request('/wallet/listproposals', {}, 'post')

    def proposal_approve(self, owner_address, proposal_id, is_add_approval=True):
        """Proposal approval

        Args:
            owner_address (str): Approve address
            proposal_id (int): proposal id
            is_add_approval (bool): Approved

        Returns:
             Approval of the proposed transaction

        """
        if not self.is_address(owner_address):
            raise InvalidTronError('Invalid address provided')

        if not isinstance(proposal_id, int) or proposal_id < 0:
            raise InvalidTronError('Invalid proposalID provided')

        return self.full_node.request('/wallet/proposalapprove', {
            'owner_address': self.address.to_hex(owner_address),
            'proposal_id': proposal_id,
            'is_add_approval': is_add_approval
        }, 'post')

    def proposal_delete(self, owner_address, proposal_id):
        """Delete proposal

        Args:
            owner_address (str): delete the person's address
            proposal_id (int): proposal id

        Results:
            Delete the proposal's transaction

        """
        if not self.is_address(owner_address):
            raise InvalidTronError('Invalid address provided')

        if not isinstance(proposal_id, int) or proposal_id < 0:
            raise InvalidTronError('Invalid proposalID provided')

        return self.full_node.request('/wallet/proposaldelete', {
            'owner_address': self.address.to_hex(owner_address),
            'proposal_id': proposal_id
        }, 'post')

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
        if not self.is_address(owner_address):
            raise InvalidTronError('Invalid address provided')

        if not isinstance(token_id, str) or len(token_id):
            raise InvalidTronError('Invalid token ID provided')

        if not isinstance(quant, int) or quant <= 0:
            raise InvalidTronError('Invalid quantity provided')

        if not isinstance(expected, int) or quant < 0:
            raise InvalidTronError('Invalid expected provided')

        return self.full_node.request('/wallet/exchangetransaction', {
            'owner_address': self.address.to_hex(owner_address),
            'exchange_id': exchange_id,
            'token_id': token_id,
            'quant': quant,
            'expected': expected
        }, 'post')

    def list_exchanges_paginated(self, limit=10, offset=0):
        """Paged query transaction pair list

        Args:
            limit (int): number of trading pairs  expected to be returned.
            offset (int): index of the starting trading pair

        """
        return self.full_node.request('/wallet/listexchangespaginated', {
            'limit': limit,
            'offset': offset
        }, 'post')

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
        if not self.is_address(owner_address):
            raise InvalidTronError('Invalid address provided')

        if isinstance(first_token_id, str) or len(first_token_id) or \
                not isinstance(second_token_id, str) or len(second_token_id):
            raise InvalidTronError('Invalid token ID provided')

        if not isinstance(first_token_balance, int) or first_token_balance <= 0 or \
                not isinstance(second_token_balance, int) or second_token_balance <= 0:
            raise InvalidTronError('Invalid amount provided')

        return self.full_node.request('/wallet/exchangecreate', {
            'owner_address': self.address.to_hex(owner_address),
            'first_token_id': first_token_id,
            'first_token_balance': first_token_balance,
            'second_token_id': second_token_id,
            'second_token_balance': second_token_balance
        }, 'post')

    def is_address(self, address):
        """Helper function that will check if a given address is valid.

        Args:
            address (str): Address to validate if it's a proper TRON address.

        """
        if not isinstance(address, str):
            return False

        if len(address) == 42:
            address = self.from_hex(address).decode('utf8')

        bc = base58.b58decode(address)
        return bc[-4:] == sha256(sha256(bc[:-4]).digest()).digest()[:4]

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
        return binascii.a2b_hex(s).decode()

    @staticmethod
    def from_ascii(string):
        return binascii.b2a_hex(bytes(string, encoding="utf8")).decode()

    @staticmethod
    def to_utf8(hex_string):
        return binascii.unhexlify(hex_string).decode()

    @staticmethod
    def from_utf8(string):
        return binascii.hexlify(bytes(string, encoding="utf8")).decode()

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
    def to_sun(amount):
        """Helper function that will convert a value in TRX to SUN.

        Args:
            amount (float): Value in TRX to convert to SUN

        """
        return math.floor(amount * 1e6)

    @staticmethod
    def from_sun(amount):
        """Helper function that will convert a value in SUN to TRX.

        Args:
            amount (int): Value in SUN to convert to TRX

        """
        return abs(amount) / 1e6

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
            'event_server': self.events.is_event_connected()
        }
