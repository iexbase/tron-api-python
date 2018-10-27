# TRON API for Python
A Python API for interacting with the Tron (TRX)

## Install

```bash
> pip3 install tronapi
```

# Creating an Instance
```python

# Specify the API endpoints:
full_node = HttpProvider('https://api.trongrid.io')
solidity_node = HttpProvider('https://api.trongrid.io')
event_server = HttpProvider('https://api.trongrid.io')
```
The provider above is optional, you can just use a url for the nodes instead, like here:
```python 
full_node = 'https://api.trongrid.io'
solidity_node = 'https://api.trongrid.io'
event_server = 'https://api.trongrid.io'
```
Now, instance a Tron class:
```python
private_key = '....'
tron = Tron(full_node, 
            solidity_node, 
            event_server, 
            private_key)         
```            
A full example:
```python
from tronapi.providers import HttpProvider
from tronapi.tron import Tron

full_node = HttpProvider('https://api.trongrid.io')
solidity_node = HttpProvider('https://api.trongrid.io')
event_server = HttpProvider('https://api.trongrid.io')

# optional
private_key = '...'

tron = Tron(full_node, 
            solidity_node, 
            event_server, 
            private_key)   


block = tron.get_current_block()
balance = tron.get_balance('TRWBqiqoFZysoAeyR1J35ibuyc8EvhUAoY', True)
```


### Cli
```bash
>>> python cli.py send from to amount private_key
>>> python cli.py --generateaddress
>>> python cli.py --node=customnode --getbalance address
```


## Donations
**Tron(TRX)**: TRWBqiqoFZysoAeyR1J35ibuyc8EvhUAoY
