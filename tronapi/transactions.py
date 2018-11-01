from tronapi import utils
from tronapi.exceptions import InvalidTronError, TronError
from tronapi.utils import string_utf8_to_hex


class TransactionBuilder(object):
    def __init__(self, tron):
        self.tron = tron

    def send_trx(self, to, amount, account):
        """Creates a transaction of transfer.
        If the recipient address does not exist, a corresponding account will be created.

        Args:
            to (str): to address
            amount (float): amount
            account (str): from address

        Returns:
            Transaction contract data

        """
        if not self.tron.is_address(to):
            raise InvalidTronError('Invalid recipient address provided')

        if not isinstance(amount, float) or amount <= 0:
            raise InvalidTronError('Invalid amount provided')

        _to = self.tron.address.to_hex(to)
        _from = self.tron.address.to_hex(account)

        if _to == _from:
            raise TronError('Cannot transfer TRX to the same account')

        return self.tron.full_node.request('/wallet/createtransaction', {
            'to_address': _to,
            'owner_address': _from,
            'amount': self.tron.to_sun(amount)
        }, 'post')

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
        if not self.tron.is_address(to):
            raise InvalidTronError('Invalid recipient address provided')

        if not isinstance(amount, float) or amount <= 0:
            raise InvalidTronError('Invalid amount provided')

        if not utils.is_string(token_id) or not len(token_id):
            raise InvalidTronError('Invalid token ID provided')

        if not self.tron.is_address(account):
            raise InvalidTronError('Invalid origin address provided')

        _to = self.tron.address.to_hex(to)
        _from = self.tron.address.to_hex(account)
        _token_id = self.tron.from_utf8(token_id)

        if _to == _from:
            raise TronError('Cannot transfer TRX to the same account')

        return self.tron.full_node.request('/wallet/transferasset', {
            'to_address': _to,
            'owner_address': _from,
            'asset_name': _token_id,
            'amount': self.tron.to_sun(amount)
        }, 'post')

    def update_account(self, account_name, account):
        """Modify account name

        Note: Username is allowed to edit only once.

        Args:
            account_name (str): name of the account
            account (str): address

        Returns:
            modified Transaction Object

        """
        if not utils.is_string(account_name):
            raise ValueError('Name must be a string')

        if not self.tron.is_address(account):
            raise TronError('Invalid origin address provided')

        response = self.tron.full_node.request('/wallet/updateaccount', {
            'account_name': string_utf8_to_hex(account_name),
            'owner_address': self.tron.address.to_hex(account)
        }, 'post')

        if 'Error' in response:
            raise Exception('This account name already exist')

        return response
