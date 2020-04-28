# --------------------------------------------------------------------
# Copyright (c) iEXBase. All rights reserved.
# Licensed under the MIT License.
# See License.txt in the project root for license information.
# --------------------------------------------------------------------

"""
    tronapi.trx
    ===============

    Work with basic methods

    :copyright: © 2018 by the iEXBase.
    :license: MIT License
"""

import math
from typing import Any

from trx_utils import is_integer, is_hex
from trx_utils.types import is_object, is_string, is_list

from tronapi.common.transactions import wait_for_transaction_id
from tronapi.contract import Contract
from tronapi.exceptions import InvalidTronError, TronError, TimeExhausted
from tronapi.module import Module
from tronapi.common.blocks import select_method_for_block
from tronapi.common.toolz import (
    assoc
)
from tronapi.common.account import Account

TRX_MESSAGE_HEADER = '\x19TRON Signed Message:\n'
ETH_MESSAGE_HEADER = '\x19Ethereum Signed Message:\n'


class Trx(Module):
    default_contract_factory = Contract

    def get_current_block(self):
        """Query the latest block"""
        return self.tron.manager.request(url='/wallet/getnowblock')

    def get_confirmed_current_block(self):
        """Query the confirmed latest block"""
        return self.tron.manager.request('/walletsolidity/getnowblock')

    def get_block(self, block: Any = None):
        """Get block details using HashString or blockNumber

        Args:
            block (Any): ID or height for the block

        """

        # If the block identifier is not specified,
        # we take the default
        if block is None:
            block = self.tron.default_block

        if block == 'latest':
            return self.get_current_block()
        elif block == 'earliest':
            return self.get_block(0)

        method = select_method_for_block(
            block,
            if_hash={'url': '/wallet/getblockbyid', 'field': 'value'},
            if_number={'url': '/wallet/getblockbynum', 'field': 'num'},
        )

        result = self.tron.manager.request(method['url'], {
            method['field']: block
        })

        if result:
            return result
        raise ValueError("The call to {method['url']} did not return a value.")

    def get_transaction_count_by_blocknum(self, num: int):
        """Query transaction's count on a specified block by height

        Args:
            num (int): block number
        """
        if not is_integer(num) or num < 0:
            raise ValueError('Invalid num provided')

        return self.tron.manager.request('/wallet/gettransactioncountbyblocknum', {
            'num': num
        })

    def get_block_transaction_count(self, block: Any):
        """Total number of transactions in a block

        Args:
            block (Any): Number or Hash Block

        """
        transaction = self.get_block(block)
        if 'transactions' not in transaction:
            raise TronError('Parameter "transactions" not found')

        return len(transaction)

    def get_transaction_from_block(self, block: Any, index: int = 0):
        """Get transaction details from Block

        Args:
            block (Any): Number or Hash Block
            index (int) Position

        """
        if not is_integer(index) or index < 0:
            raise InvalidTronError('Invalid transaction index provided')

        transactions = self.get_block(block).get('transactions')
        if not transactions or len(transactions) < index:
            raise TronError('Transaction not found in block')

        return transactions[index]

    def wait_for_transaction_id(self,
                                transaction_hash: str,
                                timeout=120,
                                poll_latency=0.2):
        """
        Waits for the transaction specified by transaction_hash
        to be included in a block, then returns its transaction receipt.

        Optionally, specify a timeout in seconds.
        If timeout elapses before the transaction is added to a block,
        then wait_for_transaction_id() raises a Timeout exception.


        Args:
            transaction_hash (str): Transaction Hash
            timeout (int): TimeOut
            poll_latency (any):  between subsequent requests

        """
        try:
            if poll_latency > timeout:
                poll_latency = timeout

            return wait_for_transaction_id(self.tron, transaction_hash, timeout, poll_latency)
        except TimeoutError:
            raise TimeExhausted(
                "Transaction {} is not in the chain, after {} seconds".format(
                    transaction_hash,
                    timeout,
                )
            )

    def get_transaction(self, transaction_id: str,
                        is_confirm: bool = False):
        """Query transaction based on id

        Args:
            transaction_id (str): transaction id
            is_confirm (bool):
        """

        method = 'walletsolidity' if is_confirm else 'wallet'
        response = self.tron.manager.request('/{}/gettransactionbyid'.format(method), {
            'value': transaction_id
        })

        if 'txID' not in response:
            raise ValueError('Transaction not found')

        return response

    def get_account_by_id(self, account_id: str, options: object):
        return self.get_account_info_by_id(account_id, options)

    def get_account_info_by_id(self, account_id: str, options: object):

        if account_id.startswith('0x'):
            account_id = id[2:]

        if 'confirmed' in options:
            return self.tron.manager.request('/walletsolidity/getaccountbyid', {
                'account_id': self.tron.toHex(text=account_id)
            })

        return self.tron.manager.request('/wallet/getaccountbyid', {
            'account_id': self.tron.toHex(text=account_id)
        })

    def get_unconfirmed_account_by_id(self, account_id: str):

        return self.get_account_info_by_id(account_id, {
            'confirmed': True
        })

    def get_account_resource(self, address=None):
        """Query the resource information of the account

        Args:
            address (str): Address

        Results:
            Resource information of the account

        """

        if address is None:
            address = self.tron.default_address.hex

        if not self.tron.isAddress(address):
            raise InvalidTronError('Invalid address provided')

        return self.tron.manager.request('/wallet/getaccountresource', {
            'address': self.tron.address.to_hex(address)
        })

    def get_account(self, address=None):
        """Query information about an account

        Args:
            address (str): Address

        """

        if address is None:
            address = self.tron.default_address.hex

        if not self.tron.isAddress(address):
            raise InvalidTronError('Invalid address provided')

        return self.tron.manager.request('/walletsolidity/getaccount', {
            'address': self.tron.address.to_hex(address)
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
            return self.tron.fromSun(response['balance'])

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
            _from = self.get_transactions_related(address, 'from', limit, offset)
            _to = self.get_transactions_related(address, 'to', limit, offset)

            filter_from = [{**i, 'direction': 'from'} for i in _from]
            filter_to = [{**i, 'direction': 'to'} for i in _to]

            callback = filter_from
            callback.extend(filter_to)
            return callback

        if address is None:
            address = self.tron.default_address.hex

        if not self.tron.isAddress(address):
            raise InvalidTronError('Invalid address provided')

        if not isinstance(limit, int) or limit < 0 or (offset and limit < 1):
            raise InvalidTronError('Invalid limit provided')

        if not isinstance(offset, int) or offset < 0:
            raise InvalidTronError('Invalid offset provided')

        path = '/walletextension/gettransactions{0}this'.format(direction)
        response = self.tron.manager.request(path, {
            'account': {
                'address': self.tron.address.to_hex(address)
            },
            'limit': limit,
            'offset': offset
        }, 'get')

        if 'transaction' in response:
            return response['transaction']
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
        response = self.tron.manager.request('/walletsolidity/gettransactioninfobyid', {
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
            address = self.tron.default_address.hex

        if not self.tron.isAddress(address):
            raise InvalidTronError('Invalid address provided')

        response = self.tron.manager.request('/wallet/getaccountnet', {
            'address': self.tron.address.to_hex(address)
        })

        free_net_limit = 0 if 'freeNetLimit' not in response else response['freeNetLimit']
        free_net_used = 0 if 'freeNetUsed' not in response else response['freeNetUsed']
        net_limit = 0 if 'NetLimit' not in response else response['NetLimit']
        net_used = 0 if 'NetUsed' not in response else response['NetUsed']

        return (free_net_limit - free_net_used) + (net_limit - net_used)

    def get_transaction_count(self):
        """Count all transactions on the network
        Note: Possible delays

        Returns:
            Total number of transactions.

        """
        response = self.tron.manager.request('/wallet/totaltransaction')
        return response.get('num')

    def send(self, to, amount, options=None):
        """Send funds to the Tron account (option 2)"""
        return self.send_transaction(to, amount, options)

    def send_trx(self, to, amount, options=None):
        """Send funds to the Tron account (option 3)"""
        return self.send_transaction(to, amount, options)

    def send_transaction(self, to, amount, options=None):
        """Send an asset to another account.
        Will create and broadcast the transaction if a private key is provided.

        Args:
            to (str): Address to send TRX to.
            amount (float): Amount of TRX to send.
            options (Any, optional): Options

        """

        if options is None:
            options = {}

        if 'from' not in options:
            options = assoc(options, 'from', self.tron.default_address.hex)

        tx = self.tron.transaction_builder.send_transaction(
            to,
            amount,
            options['from']
        )
        # If a comment is attached to the transaction,
        # in this case adding to the object
        if 'message' in options:
            tx['raw_data']['data'] = self.tron.toHex(text=str(options['message']))

        sign = self.sign(tx)
        result = self.broadcast(sign)

        return result

    def send_token(self, to, amount, token_id=None, account=None):
        """Transfer Token

        Args:
            to (str): is the recipient address
            amount (float): is the amount of token to transfer
            token_id (str): Token Name(NOT SYMBOL)
            account: (str): is the address of the withdrawal account

        Returns:
            Token transfer Transaction raw data

        """
        if account is None:
            account = self.tron.default_address.hex

        tx = self.tron.transaction_builder.send_token(
            to,
            amount,
            token_id,
            account
        )
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
            account = self.tron.default_address.hex

        transaction = self.tron.transaction_builder.freeze_balance(
            amount,
            duration,
            resource,
            account
        )
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
            account = self.tron.default_address.hex

        transaction = self.tron.transaction_builder.unfreeze_balance(
            resource,
            account
        )
        sign = self.sign(transaction)
        response = self.broadcast(sign)

        return response

    def online_sign(self, transaction: dict):
        """Online transaction signature
        Sign the transaction, the api has the risk of leaking the private key,
        please make sure to call the api in a secure environment

        Warnings:
            Do not use this in any web / user-facing applications.
            This will expose the private key.

        Args:
            transaction (dict): transaction details

        """

        if 'signature' in transaction:
            raise TronError('Transaction is already signed')

        address = self.tron.address.from_private_key(self.tron.private_key).hex.lower()
        owner_address = transaction['raw_data']['contract'][0]['parameter']['value']['owner_address']

        if address != owner_address:
            raise ValueError('Private key does not match address in transaction')

        return self.tron.manager.request('/wallet/gettransactionsign', {
            'transaction': transaction,
            'privateKey': self.tron.private_key
        })

    def sign(self, transaction: Any, use_tron: bool = True, multisig: bool = False):
        """Safe method for signing your transaction

        Warnings:
            method: online_sign() - Use only in extreme cases.

        Args:
            transaction (Any): transaction details
            use_tron (bool): is Tron header
            multisig (bool): multi sign

        """

        if is_string(transaction):
            if not is_hex(transaction):
                raise TronError('Expected hex message input')

            # Determine which header to attach to the message
            # before encrypting or decrypting
            header = TRX_MESSAGE_HEADER if use_tron else ETH_MESSAGE_HEADER
            header += str(len(transaction))

            message_hash = self.tron.keccak(text=header+transaction)

            signed_message = Account.sign_hash(self.tron.toHex(message_hash), self.tron.private_key)
            return signed_message

        if not multisig and 'signature' in transaction:
            raise TronError('Transaction is already signed')

        try:
            if not multisig:
                address = self.tron.address.from_private_key(self.tron.private_key).hex.lower()
                owner_address = transaction['raw_data']['contract'][0]['parameter']['value']['owner_address']

                if address != owner_address:
                    raise ValueError('Private key does not match address in transaction')

            # This option deals with signing of transactions, and writing to the array
            signed_tx = Account.sign_hash(
                transaction['txID'], self.tron.private_key
            )
            signature = signed_tx['signature'].hex()[2:]

            # support multi sign
            if 'signature' in transaction and is_list(transaction['signature']):
                if not transaction['signature'].index(signature):
                    transaction['signature'].append(signature)
            else:
                transaction['signature'] = [signature]

            return transaction
        except ValueError as err:
            raise InvalidTronError(err)

    def broadcast(self, signed_transaction):
        """Broadcast the signed transaction

        Args:
            signed_transaction (object): signed transaction contract data

        """
        if not is_object(signed_transaction):
            raise InvalidTronError('Invalid transaction provided')

        if 'signature' not in signed_transaction:
            raise TronError('Transaction is not signed')

        response = self.tron.manager.request('/wallet/broadcasttransaction',
                                             signed_transaction)

        if 'result' in response:
            response.update({
                'transaction': signed_transaction
            })
        return response

    def sign_and_broadcast(self, transaction: Any):
        """Sign and send to the network

        Args:
            transaction (Any): transaction details
        """
        if not is_object(transaction):
            raise TronError('Invalid transaction provided')

        signed_tx = self.sign(transaction)
        return self.broadcast(signed_tx)

    def verify_message(self, message, signed_message=None, address=None, use_tron: bool = True):
        """ Get the address of the account that signed the message with the given hash.
        You must specify exactly one of: vrs or signature

        Args:
            message (str): The message in the format "hex"
            signed_message (AttributeDict): Signature
            address (str): is Address
            use_tron (bool): is Tron header

        """
        if address is None:
            address = self.tron.default_address.base58

        if not is_hex(message):
            raise TronError('Expected hex message input')

        # Determine which header to attach to the message
        # before encrypting or decrypting
        header = TRX_MESSAGE_HEADER if use_tron else ETH_MESSAGE_HEADER
        header += str(len(message))

        message_hash = self.tron.keccak(text=header+message)
        recovered = Account.recover_hash(self.tron.toHex(message_hash), signed_message.signature)

        tron_address = '41' + recovered[2:]
        base58address = self.tron.address.from_hex(tron_address).decode()

        if base58address == address:
            return True

        raise ValueError('Signature does not match')

    def update_account(self, account_name, address=None):
        """Modify account name
        Note: Username is allowed to edit only once.

        Args:
            account_name (str): name of the account
            address (str): address

        """
        if address is None:
            address = self.tron.default_address.hex

        transaction = self.tron.transaction_builder.update_account(
            account_name,
            address
        )
        sign = self.sign(transaction)
        response = self.broadcast(sign)

        return response

    def apply_for_sr(self, url, address):
        """Apply to become a super representative
        Note: Applied to become a super representative. Cost 9999 TRX.

        Args:
            url (str): official website address
            address (str): address

        """

        if address is None:
            address = self.tron.default_address.hex

        transaction = self.tron.transaction_builder.apply_for_sr(
            url,
            address
        )
        sign = self.sign(transaction)
        response = self.broadcast(sign)

        return response

    def list_nodes(self):
        """List the nodes which the api fullnode is connecting on the network"""
        response = self.tron.manager.request('/wallet/listnodes')
        callback = map(lambda x: {
            'address': '{}:{}'.format(self.tron.toText(x['address']['host']),
                                      str(x['address']['port']))
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

        if not self.tron.isAddress(address):
            raise InvalidTronError('Invalid address provided')

        address = self.tron.address.to_hex(address)

        return self.tron.manager.request('/wallet/getassetissuebyaccount', {
            'address': address
        })

    def get_token_from_id(self, token_id: str):
        """Query token by name.

        Args:
            token_id (str): The name of the token

        """
        if not isinstance(token_id, str) or not len(token_id):
            raise InvalidTronError('Invalid token ID provided')

        return self.tron.manager.request('/wallet/getassetissuebyname', {
            'value': self.tron.toHex(text=token_id)
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

        response = self.tron.manager.request('/wallet/getblockbylimitnext', {
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

        response = self.tron.manager.request('/wallet/getblockbylatestnum', {
            'num': num
        })

        return response.get('block')

    def list_super_representatives(self):
        """Query the list of Super Representatives"""
        response = self.tron.manager.request('/wallet/listwitnesses')
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
            return self.tron.manager.request('/wallet/getassetissuelist').get('assetIssue')

        return self.tron.manager.request('/wallet/getpaginatedassetissuelist', {
            'limit': int(limit),
            'offset': int(offset)
        })

    def time_until_next_vote_cycle(self):
        """Get the time of the next Super Representative vote

        Returns:
            Number of milliseconds until the next voting time.

        """
        num = self.tron.manager.request('/wallet/getnextmaintenancetime').get('num')

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

        if not self.tron.isAddress(contract_address):
            raise InvalidTronError('Invalid contract address provided')

        return self.tron.manager.request('/wallet/getcontract', {
            'value': self.tron.address.to_hex(contract_address)
        })

    def contract(self, address=None, **kwargs):
        """Work with a contract

        Args:
            address (str): TRON Address
            **kwargs (any): details (bytecode, abi)
        """
        factory_class = kwargs.pop('contract_factory_class', self.default_contract_factory)
        contract_factory = factory_class.factory(self.tron, **kwargs)

        if address:
            return contract_factory(address)
        return contract_factory

    def validate_address(self, address, _is_hex=False):
        """Validate address

        Args:
            address (str): The address, should be in base58checksum
            _is_hex (bool): hexString or base64 format

        """
        if _is_hex:
            address = self.tron.address.to_hex(address)

        return self.tron.manager.request('/wallet/validateaddress', {
            'address': address
        })

    def get_chain_parameters(self):
        """Getting chain parameters"""
        return self.tron.manager.request('/wallet/getchainparameters')

    def get_exchange_by_id(self, exchange_id):
        """Find exchange by id

        Args:
             exchange_id (str): ID Exchange

        """

        if not isinstance(exchange_id, int) or exchange_id < 0:
            raise InvalidTronError('Invalid exchangeID provided')

        return self.tron.manager.request('/wallet/getexchangebyid', {
            'id': exchange_id
        })

    def get_list_exchangers(self):
        """Get list exchangers"""
        return self.tron.manager.request('/wallet/listexchanges')

    def get_proposal(self, proposal_id):
        """Query proposal based on id

        Args:
            proposal_id (int): ID

        """
        if not isinstance(proposal_id, int) or proposal_id < 0:
            raise InvalidTronError('Invalid proposalID provided')

        return self.tron.manager.request('/wallet/getproposalbyid', {
            'id': int(proposal_id)
        })

    def list_proposals(self):
        """Query all proposals

        Returns:
            Proposal list information

        """
        return self.tron.manager.request('/wallet/listproposals')

    def vote_proposal(self, proposal_id, has_approval, voter_address):
        """Proposal approval

        Args:
            proposal_id (int): proposal id
            has_approval (bool): Approved
            voter_address (str): Approve address

        Returns:
             Approval of the proposed transaction

        """

        if voter_address is None:
            voter_address = self.tron.default_address.hex

        transaction = self.tron.transaction_builder.vote_proposal(
            proposal_id,
            has_approval,
            voter_address
        )
        sign = self.sign(transaction)
        response = self.broadcast(sign)

        return response

    def proposal_delete(self, proposal_id: int, issuer_address: str):
        """Delete proposal

        Args:
            proposal_id (int): proposal id
            issuer_address (str): delete the person's address

        Results:
            Delete the proposal's transaction

        """
        if issuer_address is None:
            issuer_address = self.tron.default_address.hex

        transaction = self.tron.transaction_builder.delete_proposal(
            proposal_id,
            issuer_address
        )
        sign = self.sign(transaction)
        response = self.broadcast(sign)

        return response

    def list_exchanges_paginated(self, limit=10, offset=0):
        """Paged query transaction pair list

        Args:
            limit (int): number of trading pairs  expected to be returned.
            offset (int): index of the starting trading pair

        """
        return self.tron.manager.request('/wallet/listexchangespaginated', {
            'limit': limit,
            'offset': offset
        })

    def get_node_info(self):
        """Get info about thre node"""
        return self.tron.manager.request('/wallet/getnodeinfo')

    def get_token_list_name(self, token_id: str) -> any:
        """Query token list by name.

            Args:
                token_id (str): The name of the token
        """
        if not is_string(token_id):
            raise ValueError('Invalid token ID provided')

        return self.tron.manager.request('/wallet/getassetissuelistbyname', {
            'value': self.tron.toHex(text=token_id)
        })

    def get_token_by_id(self, token_id: str) -> any:
        """Query token by id.

            Args:
                token_id (str): The id of the token, it's a string
        """
        if not is_string(token_id):
            raise ValueError('Invalid token ID provided')

        return self.tron.manager.request('/wallet/getassetissuebyid', {
            'value': token_id
        })
