# -*- coding: utf-8 -*-

# Copyright 2018 iEXBase
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import binascii
from _sha256 import sha256

import base58
import math

from Crypto.Hash import keccak
from tronapi import config
from tronapi.crypto import utils
from tronapi.provider import HttpProvider


class Tron:

    def __init__(self, full_node, solidity_node=None, event_server=None, private_key=None):
        """A Python API for interacting with the Tron (TRX)

        Args:
            full_node (:obj:`str`): A provider connected to a valid full node
            solidity_node (:obj:`str`): A provider connected to a valid solidity node
            event_server (:obj:`str`, optional): Optional for smart contract events. Expects a valid event server URL
            private_key (str): Optional default private key used when signing transactions

        """
        if not solidity_node:
            solidity_node = config.DEFAULT_SOLIDITY_NODE

        if isinstance(full_node, str):
            full_node = HttpProvider(full_node)

        if isinstance(solidity_node, str):
            solidity_node = HttpProvider(solidity_node)

        if isinstance(event_server, str):
            event_server = HttpProvider(event_server)

        self.__set_full_node(full_node)
        self.__set_solidity_node(solidity_node)
        self.__set_event_server(event_server)

        self.tron_node = HttpProvider(config.DEFAULT_TRON_NODE)

        if private_key:
            self.private_key = private_key

    def __set_full_node(self, provider):
        """Check specified "full node"

        Args:
            provider (HttpProvider): full node

        """
        if not self.is_valid_provider(provider):
            raise Exception('Invalid full node provided')

        self.full_node = provider
        self.full_node.status_page = '/wallet/getnowblock'

    def __set_solidity_node(self, provider):
        """Check specified "solidity node"

        Args:
            provider (HttpProvider): solidity node

        """
        if not self.is_valid_provider(provider):
            raise Exception('Invalid solidity node provided')

        self.solidity_node = provider
        self.solidity_node.status_page = '/walletsolidity/getnowblock'

    def __set_event_server(self, server):
        """Check specified "event server"

        Args:
            server (HttpProvider): event server

        """
        if server and not self.is_valid_provider(server):
            raise Exception('Invalid event provided')

        self.event_server = server

    def is_event_connected(self):
        """
        Checks if is connected to the event server.

        Returns:
            bool: True if successful, False otherwise.

        """
        if not self.event_server:
            return False

        return self.event_server.request('/healthcheck') == 'OK'

    @staticmethod
    def is_valid_provider(provider):
        """Check connected provider

        Args:
            provider(HttpProvider): Provider

        Returns:
           True if successful, False otherwise.

        """
        return isinstance(provider, HttpProvider)

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

        if not self.event_server:
            raise Exception('No event server configured')

        if not self.is_address(contract_address):
            raise Exception('Invalid contract address provided')

        if event_name and not contract_address:
            raise Exception('Usage of event name filtering requires a contract address')

        if block_number and not event_name:
            raise Exception('Usage of block number filtering requires an event name')

        route_params = []

        if contract_address:
            route_params.append(contract_address)

        if event_name:
            route_params.append(event_name)

        if block_number:
            route_params.append(block_number)

        route = '/'.join(route_params)
        return self.event_server.request("/event/contract/{}?since={}".format(route, since))

    def get_event_transaction_id(self, tx_id):
        """Will return all events within a transactionID.

        Args:
            tx_id (str): TransactionID to query for events.

        Examples:
              >>> tron.get_event_transaction_id('660028584562b3ae687090f77e989bc7b0bc8b0a8f677524630002c06fd1d57c')

        """

        if not self.event_server:
            raise Exception('No event server configured')

        response = self.event_server.request('/event/transaction/' + tx_id)
        return response

    def get_current_block(self):
        """Query the latest block

        Returns:
            Latest block on full node
        """
        return self.full_node.request('/wallet/getnowblock')

    def get_block(self, block=None):
        """Get block details using HashString or blockNumber

        Args:
            block (int|str): Number or Hash Block

        """
        if block is None:
            raise Exception('No block identifier provided')

        if block == 'latest':
            return self.get_current_block()

        if len(block) == 64:
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
            raise Exception('Invalid block number provided')

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
            raise Exception('Parameter "transactions" not found')

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
            raise Exception('Invalid transaction index provided')

        transactions = self.get_block(block)['transactions']

        if not transactions or len(transactions) < index:
            raise Exception('Transaction not found in block')

        return transactions[index]

    def get_transaction(self, transaction_id):
        """Query transaction based on id

        Args:
            transaction_id (str): transaction id

        """
        response = self.full_node.request('/wallet/gettransactionbyid', {
            'value': transaction_id
        }, 'post')

        if not response:
            raise Exception('Transaction not found')

        return response

    def get_account_resource(self, address):
        """Query the resource information of the account

        Args:
            address (str): Address

        Results:
            Resource information of the account

        """

        if not self.is_address(address):
            raise Exception('Invalid address provided')


        return self.full_node.request('/wallet/getaccountresource', {
            'address': self.to_hex(address)
        })

    def get_account(self, address):
        """Query information about an account

        Args:
            address (str): Address

        """
        if not self.is_address(address):
            raise Exception('Invalid address provided')

        return self.solidity_node.request('/walletsolidity/getaccount', {
            'address': self.to_hex(address)
        }, 'post')

    def get_balance(self, address, from_tron=False):
        """Getting a balance

        Args:
            address (str): Address
            from_tron (bool): Convert to float format

        """
        response = self.get_account(address)

        if 'balance' not in response:
            return 0

        if from_tron:
            return self.from_tron(response['balance'])

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
            raise Exception('Invalid direction provided: Expected "to", "from" or "all"')

        if direction == 'all':
            from_direction = {'from': self.get_transactions_related(address, 'from', limit, offset)}
            to_direction = {'to': self.get_transactions_related(address, 'to', limit, offset)}

            callback = from_direction
            callback.update(to_direction)
            return callback

        if not self.is_address(address):
            raise Exception('Invalid address provided')

        if not isinstance(limit, int) or limit < 0 or (offset and limit < 1):
            raise Exception('Invalid limit provided')

        if not isinstance(offset, int) or offset < 0:
            raise Exception('Invalid offset provided')

        response = self.solidity_node.request('/walletextension/gettransactions{}this'.format(direction), {
            'account': {'address': self.to_hex(address)},
            'limit': limit,
            'offset': offset
        }, 'post')

        response.update({'direction': direction})
        return response

    def get_transactions_to_address(self, address, limit=30, offset=0):
        """Query the list of transactions received by an address

        Args:
            address (str): address
            limit (int): number of transactions expected to be returned
            offset (int): index of the starting transaction

        Returns:
            Transactions list

        """
        return self.get_transactions_related(address, 'to', limit, offset)

    def get_transactions_from_address(self, address, limit=30, offset=0):
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

    def get_band_width(self, address):
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

        if not self.is_address(address):
            raise Exception('Invalid address provided')

        return self.full_node.request('/wallet/getaccountnet', {
            'address': self.to_hex(address)
        })

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

    def send(self, from_address, to_address, amount):
        """Send funds to the Tron account (option 2)

        Args:
            from_address (str): From address
            to_address (str): To address
            amount (float): Value

        Returns:
            Returns the details of the transaction being sent.
             [result = 1] - Successfully sent

        """
        return self.send_transaction(from_address, to_address, amount)

    def send_trx(self, from_address, to_address, amount):
        """Send funds to the Tron account (option 3)

        Args:
            from_address (str): From address
            to_address (str): To address
            amount (float): Value

        Returns:
            Returns the details of the transaction being sent.
             [result = 1] - Successfully sent

        """
        return self.send_transaction(from_address, to_address, amount)

    def send_transaction(self, from_address, to_address, amount):
        """Send transaction to Blockchain

        Args:
            from_address (str): From address
            to_address (str): To address
            amount (float): Value

        Returns:
            Returns the details of the transaction being sent.
             [result = 1] - Successfully sent

        """
        if not self.private_key:
            raise Exception('Missing private key')

        if not self.is_address(to_address):
            raise Exception('Invalid address provided')


        transaction = self._create_transaction(from_address, to_address, amount)
        sign = self._sign_transaction(transaction)
        response = self._send_raw_transaction(sign)

        result = dict(sign)
        result.update(response)

        return result

    def _create_transaction(self, from_address, to_address, amount):
        """Creates a transaction of transfer.
        If the recipient address does not exist, a corresponding account will be created on the blockchain.

        Args:
            from_address (str): from address
            to_address (str): to address
            amount (float): amount

        Returns:
            Transaction contract data

        """

        if type(amount) != float or amount < 0:
            raise Exception('Invalid amount provided')

        _to = self.to_hex(to_address)
        _from = self.to_hex(from_address)

        if _to == _from:
            raise Exception('Cannot transfer TRX to the same account')

        return self.full_node.request('/wallet/createtransaction', {
            'to_address': _to,
            'owner_address': _from,
            'amount': self.to_tron(amount)
        }, 'post')

    def _sign_transaction(self, transaction):
        """Sign the transaction, the api has the risk of leaking the private key,
        please make sure to call the api in a secure environment

        Args:
            transaction (object): transaction details

        Returns:
            Signed Transaction contract data

        """
        if 'signature' in transaction:
            raise Exception('Transaction is already signed')

        return self.full_node.request('/wallet/gettransactionsign', {
            'transaction': transaction,
            'privateKey': self.private_key
        }, 'post')

    def _send_raw_transaction(self, signed):
        """Broadcast the signed transaction

        Args:
            signed (object): signed transaction contract data

        Returns:
            broadcast success or failure

        """
        if not type({}) is dict:
            raise Exception('Invalid transaction provided')

        if 'signature' not in signed:
            raise Exception('Transaction is not signed')

        return self.full_node.request('/wallet/broadcasttransaction', signed, 'post')

    def update_account(self, address, name):
        """Modify account name

        Note: Username is allowed to edit only once.

        Args:
            address (str): address
            name (str): name of the account

        Returns:
            modified Transaction Object

        """
        transaction = self.full_node.request('/wallet/updateaccount', {
            'account_name': self.string_utf8_to_hex(name),
            'owner_address': self.to_hex(address)
        })

        sign = self._sign_transaction(transaction)
        response = self._send_raw_transaction(sign)

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
            'owner_address': self.to_hex(address),
            'account_address': self.to_hex(new_account_address)
        }, 'post')

    def create_address(self, password):
        """Create address from a specified password string (NOT PRIVATE KEY)

        Args:
            password (str): Enter password

        Warning:
            Please control risks when using this API. To ensure environmental security,
            please do not invoke APIs provided by other or invoke this very API on a public network.

        Results:
            Value is the corresponding address for the password, encoded in hex.
            Convert it to base58 to use as the address.

        """
        return self.full_node.request('/wallet/createaddress', {
            'value': self.string_utf8_to_hex(password)
        }, 'post')

    def apply_for_super_representative(self, address, url):
        """Apply to become a super representative

        Note: Applied to become a super representative. Cost 9999 TRX.

        Args:
            address (str): address
            url (str): official website address

        """
        return self.full_node.request('/wallet/createwitness', {
            'owner_address': self.to_hex(address),
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
            raise Exception('Invalid address provided')

        return self.full_node.request('/wallet/getassetissuebyaccount', {
            'address': self.to_hex(address)
        }, 'post')

    def get_token_from_id(self, token_id):
        """Query token by name.

        Args:
            token_id (str): The name of the token

        """
        if isinstance(token_id, str) or not len(token_id):
            raise Exception('Invalid token ID provided')

        return self.full_node.request('/wallet/getassetissuebyname', {
            'value': self.from_utf8(token_id)
        })

    def get_block_range(self, start, end):
        """Query a range of blocks by block height

        Args:
            start (int): starting block height, including this block
            end (int): ending block height, excluding that block

        Returns:
            A list of Block Objects

        """
        if not utils.is_numeric(start) or start < 0:
            raise Exception('Invalid start of range provided')

        if not utils.is_numeric(end) or end <= start:
            raise Exception('Invalid end of range provided')

        return self.full_node.request('/wallet/getblockbylimitnext', {
            'startNum': int(start),
            'endNum': int(end) + 1
        }, 'post')['block']

    def get_latest_blocks(self, limit=1):
        """Query the latest blocks

        Args:
            limit (int): the number of blocks to query

        Returns:
            A list of Block Objects

        """
        if not utils.is_numeric(limit) or limit <= 0:
            raise Exception('Invalid limit provided')

        return self.full_node.request('/wallet/getblockbylatestnum', {
            'limit': limit
        }, 'post')['block']

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
            raise Exception('Invalid limit provided')

        if not utils.is_numeric(offset) or offset < 0:
            raise Exception('Invalid offset provided')

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
            exit('Failed to get time until next vote cycle')

        return math.floor(num / 1000)

    def get_contract(self, contract_address):
        """Queries a contract's information from the blockchain.

        Args:
            contract_address (str): contract address

        Returns:
            SmartContract object.

        """

        if not self.is_address(contract_address):
            raise Exception('Invalid contract address provided')

        contract_address = self.to_hex(contract_address)

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
            address = self.to_hex(address)

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
        return self.full_node.request('/wallet/generateaddress', {}, 'post')

    def get_node_map(self):
        """Getting a map of all available nodes"""
        return self.tron_node.request('/api/v2/node/nodemap')

    def get_balance_info(self):
        """Balance Information"""
        return self.tron_node.request('/api/v2/node/balance_info')

    def get_chain_parameters(self):
        """Getting chain parameters"""
        return self.full_node.request('/wallet/getchainparameters', {}, 'post')

    def get_exchange_by_id(self, exchange_id):
        """Find exchange by id

        Args:
             exchange_id (str): ID Exchange
        """

        if not isinstance(exchange_id, int) or exchange_id < 0:
            raise Exception('Invalid exchangeID provided')

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
            raise Exception('Invalid proposalID provided')

        return self.full_node.request('/wallet/getproposalbyid', {
            'id': int(proposal_id)
        }, 'post')

    def list_proposals(self):
        """Query all proposals

        Returns:
            Proposal list information

        """
        return self.full_node.request('/wallet/listproposals', {}, 'post')

    def exchange_transaction(self, owner_address, exchange_id, token_id, quant, expected):
        """ Exchanges a transaction.

        Args:
            owner_address (str):  Address of the creator of the transaction pair
            exchange_id (str): transaction pair id
            token_id (str): The id of the sold token
            quant (int): the number of tokens sold
            expected (int): the number of tokens expected to be bought

        """
        if not self.is_address(owner_address):
            raise Exception('Invalid address provided')

        if not isinstance(token_id, str) or len(token_id):
            raise Exception('Invalid token ID provided')

        if not isinstance(quant, int) or quant <= 0:
            raise Exception('Invalid quantity provided')

        if not isinstance(expected, int) or quant < 0:
            raise Exception('Invalid expected provided')

        return self.full_node.request('/wallet/exchangetransaction', {
            'owner_address': self.to_hex(owner_address),
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

    def is_connected(self):
        """Check all connected nodes"""

        return {
            'full_node': self.full_node.is_connected(),
            'solidity_node': self.solidity_node.is_connected(),
            'event_server': self.is_event_connected()
        }
