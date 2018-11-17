# --------------------------------------------------------------------------------------------
# Copyright (c) iEXBase. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from datetime import datetime, timedelta

from tronapi.exceptions import InvalidTronError, TronError
from tronapi.utils.help import is_valid_url
from tronapi.utils.types import is_string, is_integer, is_boolean

DEFAULT_TIME = datetime.now()
START_DATE = int(DEFAULT_TIME.timestamp() * 1000)


class TransactionBuilder(object):
    def __init__(self, tron):
        self.tron = tron

    def send_transaction(self, to, amount, account):
        """Creates a transaction of transfer.
        If the recipient address does not exist, a corresponding account will be created.

        Args:
            to (str): to address
            amount (float): amount
            account (str): from address

        Returns:
            Transaction contract data

        """
        if not self.tron.isAddress(to):
            raise InvalidTronError('Invalid recipient address provided')

        if not isinstance(amount, float) or amount <= 0:
            raise InvalidTronError('Invalid amount provided')

        _to = self.tron.address.to_hex(to)
        _from = self.tron.address.to_hex(account)

        if _to == _from:
            raise TronError('Cannot transfer TRX to the same account')

        response = self.tron.manager.request('/wallet/createtransaction', {
            'to_address': _to,
            'owner_address': _from,
            'amount': self.tron.toSun(amount)
        })

        return response

    def send_token(self, to, amount, token_id, account):
        """Transfer Token

        Args:
            to (str): is the recipient address
            amount (float): is the amount of token to transfer
            token_id (str): Token Name(NOT SYMBOL)
            account: (str): is the address of the withdrawal account

        Returns:
            Token transfer Transaction raw data

        """
        if not self.tron.isAddress(to):
            raise InvalidTronError('Invalid recipient address provided')

        if not isinstance(amount, float) or amount <= 0:
            raise InvalidTronError('Invalid amount provided')

        if not is_string(token_id) or not len(token_id):
            raise InvalidTronError('Invalid token ID provided')

        if not self.tron.isAddress(account):
            raise InvalidTronError('Invalid origin address provided')

        _to = self.tron.address.to_hex(to)
        _from = self.tron.address.to_hex(account)
        _token_id = self.tron.toHex(text=token_id)

        if _to == _from:
            raise TronError('Cannot transfer TRX to the same account')

        return self.tron.manager.request('/wallet/transferasset', {
            'to_address': _to,
            'owner_address': _from,
            'asset_name': _token_id,
            'amount': self.tron.toSun(amount)
        })

    def freeze_balance(self, amount, duration, resource, account):
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

        if resource not in ('BANDWIDTH', 'ENERGY',):
            raise InvalidTronError('Invalid resource provided: Expected "BANDWIDTH" or "ENERGY"')

        if not is_integer(amount) or amount <= 0:
            raise InvalidTronError('Invalid amount provided')

        if not is_integer(duration) or duration < 3:
            raise InvalidTronError('Invalid duration provided, minimum of 3 days')

        if not self.tron.isAddress(account):
            raise InvalidTronError('Invalid address provided')

        response = self.tron.manager.request('/wallet/freezebalance', {
            'owner_address': self.tron.address.to_hex(account),
            'frozen_balance': self.tron.toSun(amount),
            'frozen_duration': int(duration),
            'resource': resource
        })

        if 'Error' in response:
            raise TronError(response['Error'])

        return response

    def unfreeze_balance(self, resource='BANDWIDTH', account=None):

        if resource not in ('BANDWIDTH', 'ENERGY',):
            raise InvalidTronError('Invalid resource provided: Expected "BANDWIDTH" or "ENERGY"')

        if not self.tron.isAddress(account):
            raise InvalidTronError('Invalid address provided')

        response = self.tron.manager.request('/wallet/unfreezebalance', {
            'owner_address': self.tron.address.to_hex(account),
            'resource': resource
        })

        if 'Error' in response:
            raise ValueError(response['Error'])

        return response

    def apply_for_sr(self, url, address):
        """Apply to become a super representative

        Args:
            url (str): official website address
            address (str): address

        """
        if not self.tron.isAddress(address):
            raise TronError('Invalid address provided')

        if not is_valid_url(url):
            raise TronError('Invalid url provided')

        return self.tron.manager.request('/wallet/createwitness', {
            'owner_address': self.tron.address.to_hex(address),
            'url': self.tron.toHex(text=url)
        })

    def vote_proposal(self, proposal_id, has_approval, voter_address):
        """Proposal approval

        Args:
            proposal_id (int): proposal id
            has_approval (bool): Approved
            voter_address (str): Approve address

        """
        if not self.tron.isAddress(voter_address):
            raise TronError('Invalid voter_address address provided')

        if not is_integer(proposal_id) or proposal_id < 0:
            raise TronError('Invalid proposal_id provided')

        if not is_boolean(has_approval):
            raise TronError('Invalid has_approval provided')

        return self.tron.manager.request('/wallet/proposalapprove', {
            'owner_address': self.tron.address.to_hex(voter_address),
            'proposal_id': int(proposal_id),
            'is_add_approval': bool(has_approval)
        })

    def delete_proposal(self, proposal_id: int, issuer_address: str):
        """Delete proposal

        Args:
            proposal_id (int): proposal id
            issuer_address (str): delete the person's address

        Results:
            Delete the proposal's transaction

        """
        if not self.tron.isAddress(issuer_address):
            raise InvalidTronError('Invalid issuer_address provided')

        if not isinstance(proposal_id, int) or proposal_id < 0:
            raise InvalidTronError('Invalid proposal_id provided')

        return self.tron.manager.request('/wallet/proposaldelete', {
            'owner_address': self.tron.address.to_hex(issuer_address),
            'proposal_id': int(proposal_id)
        })

    def update_account(self, account_name, account):
        """Modify account name

        Note: Username is allowed to edit only once.

        Args:
            account_name (str): name of the account
            account (str): address

        Returns:
            modified Transaction Object

        """
        if not is_string(account_name):
            raise ValueError('Name must be a string')

        if not self.tron.isAddress(account):
            raise TronError('Invalid origin address provided')

        response = self.tron.manager.request('/wallet/updateaccount', {
            'account_name': self.tron.toHex(text=account_name),
            'owner_address': self.tron.address.to_hex(account)
        })

        return response

    def create_trx_exchange(self,
                            token_name: str,
                            token_balance: int,
                            trx_balance: int,
                            account):
        """Create an exchange between a token and TRX.
        Token Name should be a CASE SENSITIVE string.
        Note: PLEASE VERIFY THIS ON TRONSCAN.

        Args:
            token_name (str): Token Name
            token_balance (int): balance of the first token
            trx_balance (int): balance of the second token
            account (str): Owner Address
        """

        if not self.tron.isAddress(account):
            raise TronError('Invalid address provided')

        if not len(token_name):
            raise TronError('Invalid tokenName provided')

        if token_balance <= 0 or trx_balance <= 0:
            raise TronError('Invalid amount provided')

        return self.tron.manager.request('/wallet/exchangecreate', {
            'owner_address': self.tron.address.to_hex(account),
            'first_token_id': self.tron.toHex(text=token_name),
            'first_token_balance': token_balance,
            'second_token_id': '5f',
            'second_token_balance': trx_balance
        })

    def create_token(self, **kwargs):
        """Issue Token

        Issuing a token on the TRON Protocol can be done by anyone
        who has at least 1024 TRX in their account.
        When a token is issued it will be shown on the token overview page.
        Users can then participate within the issuing time and exchange their
        TRX for tokens.After issuing the token your account will
        receive the amount of tokens equal to the total supply.
        When other users exchange their TRX for tokens then the tokens
        will be withdrawn from your account and you will receive
        TRX equal to the specified exchange rate.


        Args:
            **kwargs: Fill in the required parameters

        Examples:

            >>> start_func = datetime.now()
            >>> start = int(start_func.timestamp() * 1000)
            >>>
            >>> end_func = datetime.now() + timedelta(days=2)
            >>> end = int(end_func.timestamp() * 1000)
            >>>
            >>> opt = {
            >>>     'name': 'Tron',
            >>>     'abbreviation': 'TRX',
            >>>     'description': 'Hello World',
            >>>     'url': 'https://github.com',
            >>>     'totalSupply': 25000000,
            >>>     'frozenAmount': 1,
            >>>     'frozenDuration': 2,
            >>>     'freeBandwidth': 10000,
            >>>     'freeBandwidthLimit': 10000,
            >>>     'saleStart': start,
            >>>     'saleEnd': end,
            >>>     'voteScore': 1
            >>> }

        """
        issuer_address = kwargs.setdefault(
            'issuer_address', self.tron.default_address.hex
        )

        if not self.tron.isAddress(issuer_address):
            raise TronError('Invalid issuer address provided')

        total_supply = kwargs.setdefault('totalSupply', 0)
        trx_ratio = kwargs.setdefault('trxRatio', 1)
        token_ratio = kwargs.setdefault('tokenRatio', 1)
        sale_start = kwargs.setdefault(
            'saleStart', START_DATE
        )
        free_bandwidth = kwargs.setdefault('freeBandwidth', 0)
        free_bandwidth_limit = kwargs.setdefault('freeBandwidthLimit', 0)
        frozen_amount = kwargs.setdefault('frozenAmount', 0)
        frozen_duration = kwargs.setdefault('frozenDuration', 0)
        vote_score = kwargs.setdefault('voteScore', 0)

        if not is_string(kwargs.get('name')):
            raise ValueError('Invalid token name provided')

        if not is_string(kwargs.get('abbreviation')):
            raise ValueError('Invalid token abbreviation provided')

        if not is_integer(total_supply) or total_supply <= 0:
            raise ValueError('Invalid supply amount provided')

        if not is_integer(trx_ratio) or trx_ratio <= 0:
            raise ValueError('TRX ratio must be a positive integer')

        if not is_integer(token_ratio) or token_ratio <= 0:
            raise ValueError('Token ratio must be a positive integer')

        if not is_integer(vote_score) or vote_score <= 0:
            raise ValueError('Invalid vote score provided')

        if not is_integer(sale_start) or sale_start < START_DATE:
            raise ValueError('Invalid sale start timestamp provided')

        if not is_integer(kwargs.get('saleEnd')) or \
                kwargs.get('saleEnd') <= sale_start:
            raise ValueError('Invalid sale end timestamp provided')

        if not is_string(kwargs.get('description')):
            raise ValueError('Invalid token description provided')

        if not is_valid_url(kwargs.get('url')):
            raise ValueError('Invalid token url provided')

        if not is_integer(free_bandwidth) or free_bandwidth < 0:
            raise ValueError('Invalid free bandwidth amount provided')

        if not is_integer(free_bandwidth_limit) or free_bandwidth_limit < 0 \
                or (free_bandwidth and not free_bandwidth_limit):
            raise ValueError('Invalid free bandwidth limit provided')

        if not is_integer(frozen_amount) or frozen_amount < 0 \
                or (not frozen_duration and frozen_amount):
            raise ValueError('Invalid frozen supply provided')

        if not is_integer(frozen_duration) or frozen_duration < 0 \
                or (frozen_duration and not frozen_amount):
            raise ValueError('Invalid frozen duration provided')

        frozen_supply = {
            'frozen_amount': int(frozen_amount),
            'frozen_days': int(frozen_duration)
        }

        response = self.tron.manager.request('/wallet/createassetissue', {
            'owner_address': self.tron.address.to_hex(issuer_address),
            'name': self.tron.toHex(text=kwargs.get('name')),
            'abbr': self.tron.toHex(text=kwargs.get('abbreviation')),
            'description': self.tron.toHex(text=kwargs.get('description')),
            'url': self.tron.toHex(text=kwargs.get('url')),
            'total_supply': int(total_supply),
            'trx_num': int(trx_ratio),
            'num': int(token_ratio),
            'start_time': int(sale_start),
            'end_time': int(kwargs.get('saleEnd')),
            'free_asset_net_limit': int(free_bandwidth),
            'public_free_asset_net_limit': int(free_bandwidth_limit),
            'frozen_supply': frozen_supply,
            'vote_score': vote_score
        })

        return response

