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

"""
    Tron API from Python
"""

import base58
import math

from tronapi import config
from tronapi.crypto import utils
from tronapi.provider import HttpProvider


class Tron:

    def __init__(self, full_node, solidity_node=None, private_key=None):

        if isinstance(full_node, str):
            full_node = HttpProvider(full_node)

        if isinstance(solidity_node, str):
            solidity_node = HttpProvider(solidity_node)

        self.full_node = full_node
        self.solidity_node = solidity_node
        self.tron_node = HttpProvider(config.DEFAULT_TRON_NODE)

        if private_key:
            self.private_key = private_key

    @staticmethod
    def is_valid_provider(provider):
        """Check connected provider

        Args:
            provider(str): Provider

        Returns:
           True if successful, False otherwise.

        """
        return isinstance(provider, HttpProvider)

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

        if type(block) is str:
            return self.get_block_by_hash(block)

        return self.get_block_by_number(block)

    def get_block_by_hash(self, hash_block):
        """Query block by ID

        Args:
            hash_block (str): Block ID

        Returns:
            Block Object

        """
        return self.full_node.request('/wallet/getblockbyid', {
            'value': hash_block
        })

    def get_block_by_number(self, block_id):
        """Query block by height

        Args:
            block_id (int): height of the block

        Returns:
            Block object

        """
        if not utils.is_integer(block_id) or block_id < 0:
            raise Exception('Invalid block number provided')

        return self.full_node.request('/wallet/getblockbynum', {
            'num': int(block_id)
        })

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
        if not utils.is_integer(index) or index < 0:
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

    def get_account(self, address):
        """Query information about an account

        Args:
            address (str): Address

        """
        return self.full_node.request('/wallet/getaccount', {
            'address': self.to_hex(address)
        }, 'post')

    def get_balance(self, address, from_tron=False):
        """Getting a balance

        Args:
            address (str): Address
            from_tron (bool): Convert to float format

        """
        response = self.get_account(address)
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
        return self.full_node.request('/wallet/listnodes')

    def get_tokens_issued_by_address(self, address):
        """List the tokens issued by an account.

        Args:
            address (str): address

        Returns:
            The token issued by the account.
            An account can issue only one token.

        """
        return self.full_node.request('/wallet/getassetissuebyaccount', {
            'address': self.to_hex(address)
        }, 'post')

    def get_token_from_id(self, token_id):
        """Query token by name.

        Args:
            token_id (str): The name of the token

        """
        return self.full_node.request('/wallet/getassetissuebyname', {
            'value': self.string_utf8_to_hex(token_id)
        })

    def get_block_range(self, start, end):
        """Query a range of blocks by block height

        Args:
            start (int): starting block height, including this block
            end (int): ending block height, excluding that block

        Returns:
            A list of Block Objects

        """
        if not utils.is_integer(start) or start < 0:
            raise Exception('Invalid start of range provided')

        if not utils.is_integer(end) or end <= start:
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
        if not utils.is_integer(limit) or limit <= 0:
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
        return self.full_node.request('/wallet/listwitnesses')['witnesses']

    def list_tokens(self, limit=0, offset=0):
        """Query the list of Tokens with pagination

        Args:
            limit (int): index of the starting Token
            offset (int): number of Tokens expected to be returned

        Returns:
            List of Tokens

        """
        if not utils.is_integer(limit) or (limit and offset < 1):
            raise Exception('Invalid limit provided')

        if not utils.is_integer(offset) or offset < 0:
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
        return self.full_node.request('/wallet/generateaddress')

    def get_node_map(self):
        """Getting a map of all available nodes"""
        return self.tron_node.request('/api/v2/node/nodemap')

    def get_balance_info(self):
        """Balance Information"""
        return self.tron_node.request('/api/v2/node/balance_info')

    def get_list_exchangers(self):
        """Getting a list of exchangers"""
        return self.full_node.request('/wallet/listexchanges', {}, 'post')

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

    def is_connected(self):
        """Check all connected nodes"""
        full_node = False
        solidity_node = False
        tron_node = False

        if self.full_node:
            full_node = self.full_node.is_connected()

        if self.solidity_node:
            solidity_node = self.solidity_node.is_connected()

        if self.tron_node:
            tron_node = self.tron_node.is_connected()

        return {
            'full_node': full_node,
            'solidity_node': solidity_node,
            'tron_node': tron_node
        }
