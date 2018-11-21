import json
import logging

from tronapi import Tron

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

full_node = 'https://api.trongrid.io'
solidity_node = 'https://api.trongrid.io'
event_server = 'https://api.trongrid.io/'
private_key = 'da146374a75310b9666e834ee4ad0866d6f4035967bfc76217c5a495fff9f0d0'

tron = Tron(full_node=full_node,
            solidity_node=solidity_node,
            event_server=event_server)


account = tron.create_account
is_valid = bool(tron.isAddress(account.address.hex))


logger.debug('Generated account: ')
logger.debug('- Private Key: ' + account.private_key)
logger.debug('- Public Key: ' + account.public_key)
logger.debug('- Address: ')
logger.debug('-- Base58: ' + account.address.base58)
logger.debug('-- Hex: ' + account.address.hex)
logger.debug('-- isValid: ' + str(is_valid))
logger.debug('-----------')

current_block = tron.trx.get_current_block()
logger.debug('Current block: ')
logger.debug(json.dumps(current_block, indent=2))
logger.debug('-----------')

previous_block = tron.trx.get_block(0)

logger.debug('Previous block #52: ')
logger.debug(json.dumps(previous_block, indent=2))
logger.debug('-----------')


genesis_block_count = tron.trx.get_block_transaction_count('earliest')
logger.debug('Genesis Block Transaction Count: ')
logger.debug('Transactions:' + str(genesis_block_count))
logger.debug('-----------')

transaction = tron.trx.get_transaction('757a14cef293c69b1cf9b9d3d19c2e40a330c640b05c6ffa4d54609a9628758c')

logger.debug('Transaction: ')
logger.debug('- Hash: ' + transaction['txID'])
logger.debug('- Transaction: ' + json.dumps(transaction, indent=2))
logger.debug('-----------')


account_info = tron.trx.get_account('TKLnCNY5EsLNCvCXQTCn1dtqvc6vHhJUyJ')

logger.debug('Account information: ')
logger.debug('- Address: TKLnCNY5EsLNCvCXQTCn1dtqvc6vHhJUyJ')
logger.debug('- Account:' + json.dumps(account_info, indent=2))
logger.debug('-----------')


balance = tron.trx.get_account('TKLnCNY5EsLNCvCXQTCn1dtqvc6vHhJUyJ')

logger.debug('Account balance: ')
logger.debug('- Address: TKLnCNY5EsLNCvCXQTCn1dtqvc6vHhJUyJ')
logger.debug('- Account:' + json.dumps(balance, indent=2))
logger.debug('-----------')


band_width = tron.trx.get_band_width('TKLnCNY5EsLNCvCXQTCn1dtqvc6vHhJUyJ')

logger.debug('Account bandwidth: ')
logger.debug('- Address: TKLnCNY5EsLNCvCXQTCn1dtqvc6vHhJUyJ')
logger.debug('- Bandwidth:' + json.dumps(band_width, indent=2))
logger.debug('-----------')


list_nodes = tron.trx.list_nodes()

logger.debug('List of full nodes: ')
logger.debug('- Node Count:' + str(len(list_nodes)))
logger.debug('- Nodes:' + json.dumps(list_nodes, indent=2))
logger.debug('-----------')


block_ids = tron.trx.get_block_range(30, 35)
block = list(map(lambda x: {'id': x['block_header']['raw_data']['number'] or 0}, block_ids))

logger.debug('Block IDs between 30 and 35: ')
logger.debug('- Block Range: [ 30, 35 ]')
logger.debug('- Blocks IDs:' + json.dumps(block, indent=2))
logger.debug('-----------')


# send = tron.send_trx('TGEJj8eus46QMHPgWQe1FJ2ymBXRm96fn1', 10)
# logger.debug('Send TRX transaction: ')
# logger.debug('- Result: ' + json.dumps(send, indent=2))
# logger.debug('-----------')


event_result = tron.get_event_result('TGEJj8eus46QMHPgWQe1FJ2ymBXRm96fn1', 0, 'Notify')

logger.debug('Event result:')
logger.debug('Contract Address: TGEJj8eus46QMHPgWQe1FJ2ymBXRm96fn1')
logger.debug('Event Name: Notify')
logger.debug('Block Number: 32162')
logger.debug('- Events: ' + json.dumps(event_result, indent=2))


event_by_transaction_id = tron.get_event_transaction_id('32d7efe5f70c044bcd831f21f911209a7abf4ed0d5934b2c1b804e108008cd43')

logger.debug('Specific event result:')
logger.debug('Transaction: 32d7efe5f70c044bcd831f21f911209a7abf4ed0d5934b2c1b804e108008cd43')
logger.debug('- Events: ' + json.dumps(event_by_transaction_id, indent=2))


first_transaction = tron.trx.get_transaction_from_block(0, 0)

logger.debug('First transaction from block 0')
logger.debug('- Transaction: ' + json.dumps(first_transaction, indent=2))

