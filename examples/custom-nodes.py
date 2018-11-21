from tronapi import Tron
from tronapi import HttpProvider

full_node = HttpProvider('https://api.trongrid.io')
solidity_node = HttpProvider('https://api.trongrid.io')
event_server = HttpProvider('https://api.trongrid.io')

# option 1
tron = Tron(full_node=full_node,
            solidity_node=solidity_node,
            event_server=event_server)

# option 2
tron_v2 = Tron()

# option 3
tron_v3 = Tron(
    default_address='TRWBqiqoFZysoAeyR1J35ibuyc8EvhUAoY',
    private_key='...'
)
