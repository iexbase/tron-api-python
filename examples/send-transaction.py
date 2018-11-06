from tronapi import Tron
from tronapi import HttpProvider

full_node = HttpProvider('https://api.trongrid.io')
solidity_node = HttpProvider('https://api.trongrid.io')
event_server = HttpProvider('https://api.trongrid.io')
tron = Tron(full_node,
            solidity_node,
            event_server)
tron.private_key = 'private_key'
tron.default_address = 'default address'

result = tron.trx.send('ToAddress', 1)

# Получаем результат
print(result)
