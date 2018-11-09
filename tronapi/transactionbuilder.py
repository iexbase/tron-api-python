# --------------------------------------------------------------------------------------------
# Copyright (c) iEXBase. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from tronapi.exceptions import InvalidTronError, TronError
from tronapi.utils.help import is_valid_url
from tronapi.utils.types import is_string, is_integer, is_boolean


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
