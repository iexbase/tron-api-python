import base58

from tron.crypto import utils
from tron.providers.http import Http
import math


class Tron:

    def __init__(self, full_node, solidity_node=None, private_key=None):

        self.full_node = Http(full_node)
        self.solidity_node = solidity_node
        self.private_key = private_key

    def get_current_block(self):
        return self.full_node.request('/wallet/getnowblock')

    def get_block(self, block=None):

        if block is None:
            exit('No block identifier provided')

        if block == 'latest':
            return self.get_current_block()

        if type(block) is str:
            return self.get_block_by_hash(block)

        return self.get_block_by_number(block)

    def get_block_by_hash(self, hash_block):
        return self.full_node.request('/wallet/getblockbyid', {
            'value': hash_block
        })

    def get_block_by_number(self, block_id):

        if not utils.is_integer(block_id) or block_id < 0:
            exit('Invalid block number provided')

        return self.full_node.request('/wallet/getblockbynum', {
            'num': int(block_id)
        })

    def get_block_transaction_count(self, block=None):
        transaction = self.get_block(block)['transactions']

        if transaction == 0:
            return 0

        return len(transaction)

    def get_transaction_from_block(self, block=None, index=0):

        if not utils.is_integer(index) or index < 0:
            exit('Invalid transaction index provided')

        transactions = self.get_block(block)['transactions']

        if not transactions or len(transactions) < index:
            exit('Transaction not found in block')

        return transactions[index]

    def get_transaction(self, transaction_id):

        response: object = self.full_node.request('/wallet/gettransactionbyid', {
            'value': transaction_id
        }, 'post')

        if not response:
            exit('Transaction not found')

        return response

    def get_account(self, address):
        return self.full_node.request('/wallet/getaccount', {
            'address': self.to_hex(address)
        }, 'post')

    def get_balance(self, address):
        response = self.get_account(address)

        return response['balance']

    def get_band_width(self, address):
        return self.full_node.request('/wallet/getaccountnet', {
            'address': self.to_hex(address)
        })

    def get_transaction_count(self):
        response = self.full_node.request('/wallet/totaltransaction')

        return response['num']

    def send_transaction(self, from_address, to_address, amount):

        if not self.private_key:
            exit('Missing private key')

        transaction = self._create_transaction(from_address, to_address, amount)
        sign = self._sign_transaction(transaction)
        response = self._send_raw_transaction(sign)

        result = dict(sign)
        result.update(response)

        return result

    def _create_transaction(self, from_address, to_address, amount):
        return self.full_node.request('/wallet/createtransaction', {
            'to_address': self.to_hex(to_address),
            'owner_address': self.to_hex(from_address),
            'amount': self.to_tron(amount)
        }, 'post')

    def _sign_transaction(self, transaction):

        if 'signature' in transaction:
            exit('Transaction is already signed')

        return self.full_node.request('/wallet/gettransactionsign', {
            'transaction': transaction,
            'privateKey': self.private_key
        }, 'post')

    def _send_raw_transaction(self, signed):
        if not type({}) is dict:
            exit('Invalid transaction provided')

        if 'signature' not in signed:
            exit('Transaction is not signed')

        return self.full_node.request('/wallet/broadcasttransaction', signed, 'post')

    def update_account(self, address, name):

        transaction = self.full_node.request('/wallet/updateaccount', {
            'account_name': self.string_utf8_to_hex(name),
            'owner_address': self.to_hex(address)
        })

        sign = self._sign_transaction(transaction)
        response = self._send_raw_transaction(sign)

        return response

    def register_account(self, address, new_account_address):
        return self.full_node.request('/wallet/createaccount', {
            'owner_address': self.to_hex(address),
            'account_address': self.to_hex(new_account_address)
        }, 'post')

    def apply_for_super_representative(self, address, url):
        return self.full_node.request('/wallet/createwitness', {
            'owner_address': self.to_hex(address),
            'url': self.string_utf8_to_hex(url)
        }, 'post')

    def list_nodes(self):
        return self.full_node.request('/wallet/listnodes')

    def get_tokens_issued_by_address(self, address):
        return self.full_node.request('/wallet/getassetissuebyaccount', {
            'address': self.to_hex(address)
        }, 'post')

    def get_token_from_id(self, token_id):
        return self.full_node.request('/wallet/getassetissuebyname', {
            'value': self.string_utf8_to_hex(token_id)
        })

    def get_block_range(self, start, end):

        if not utils.is_integer(start) or start < 0:
            exit('Invalid start of range provided')

        if not utils.is_integer(end) or end <= start:
            exit('Invalid end of range provided')

        return self.full_node.request('/wallet/getblockbylimitnext', {
            'startNum': int(start),
            'endNum': int(end) + 1
        }, 'post')['block']

    def get_latest_blocks(self, limit=1):

        if not utils.is_integer(limit) or limit <= 0:
            exit('Invalid limit provided')

        return self.full_node.request('/wallet/getblockbylatestnum', {
            'limit': limit
        }, 'post')['block']

    def list_super_representatives(self):
        return self.full_node.request('/wallet/listwitnesses')['witnesses']

    def list_tokens(self, limit=0, offset=0):

        if not utils.is_integer(limit) or (limit and offset < 1):
            exit('Invalid limit provided')

        if not utils.is_integer(offset) or offset < 0:
            exit('Invalid offset provided')

        if not limit:
            return self.full_node.request('/wallet/getassetissuelist')['assetIssue']

        return self.full_node.request('/wallet/getpaginatedassetissuelist', {
            'limit': int(limit),
            'offset': int(offset)
        }, 'post')

    def time_until_next_vote_cycle(self):
        num = self.full_node.request('/wallet/getnextmaintenancetime')['num']

        if num == -1:
            exit('Failed to get time until next vote cycle')

        return math.floor(num / 1000)

    def validate_address(self, address, hex=False):

        if hex:
            address = self.to_hex(address)

        return self.full_node.request('/wallet/validateaddress', {
            'address': address
        }, 'post')

    def generate_address(self):
        return self.full_node.request('/wallet/generateaddress')

    @staticmethod
    def string_utf8_to_hex(name):
        return bytes(name, encoding='utf-8').hex()

    @staticmethod
    def to_tron(amount):
        return abs(amount) * pow(10, 6)

    @staticmethod
    def from_tron(amount):
        return abs(amount) / pow(10, 6)

    @staticmethod
    def to_hex(address):
        return base58.b58decode_check(address).hex().upper()

    @staticmethod
    def from_hex(address):
        string = bytes.fromhex(address)

        return base58.b58encode_check(string)
