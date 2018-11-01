from tronapi import utils
from tronapi.exceptions import TronError, InvalidTronError
from tronapi.provider import HttpProvider


class Event(object):
    def __init__(self, tron, event_server):
        self.tron = tron

        if utils.is_string(event_server):
            event_server = HttpProvider(event_server)

        self.event_server = event_server

    def is_event_connected(self) -> bool:
        """
        Checks if is connected to the event server.

        Returns:
            bool: True if successful, False otherwise.

        """
        if not self.event_server:
            return False

        return bool(self.event_server.request(method='GET', url='/healthcheck') == 'OK')

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
            raise TronError('No event server configured')

        if not self.tron.is_address(contract_address):
            raise InvalidTronError('Invalid contract address provided')

        if event_name and not contract_address:
            raise TronError('Usage of event name filtering requires a contract address')

        if block_number and not event_name:
            raise TronError('Usage of block number filtering requires an event name')

        route_params = []

        if contract_address:
            route_params.append(contract_address)

        if event_name:
            route_params.append(event_name)

        if block_number:
            route_params.append(block_number)

        route = '/'.join(route_params)

        return self.event_server.request("/event/contract/{0}?since={1}".format(route, since))

    def get_event_transaction_id(self, tx_id):
        """Will return all events within a transactionID.

        Args:
            tx_id (str): TransactionID to query for events.

        Examples:
            >>> tron.get_event_transaction_id('660028584562b3ae687090f77e989bc7b0bc8b0a8f677524630002c06fd1d57c')

        """

        if not self.event_server:
            raise TronError('No event server configured')

        response = self.event_server.request('/event/transaction/' + tx_id)
        return response
