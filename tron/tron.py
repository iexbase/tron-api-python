from tron import crypto
from tron.crypto import utils
from tron.providers.http import Http
import math


class Tron:

    def __init__(self, full_node, solidity_node, private_key=None):

        # if not type(full_node) is str:
        #     exit('sadsa')

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