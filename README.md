# TRON API for Python
A Python API for interacting with the Tron (TRX)

[![Software License](https://img.shields.io/badge/license-MIT-brightgreen.svg)](LICENSE)
[![Requirements Status](https://requires.io/github/iexbase/tron-api-python/requirements.svg?branch=master)](https://requires.io/github/iexbase/tron-api-python/requirements/?branch=master)
[![Coverage Status](https://coveralls.io/repos/github/iexbase/tron-api-python/badge.svg?branch=master)](https://coveralls.io/github/iexbase/tron-api-python?branch=master)
[![Build Status](https://api.travis-ci.com/iexbase/tron-api-python.svg?branch=master)](https://travis-ci.com/iexbase/tron-api-python)
[![Issues](https://img.shields.io/github/issues/iexbase/tron-api-python.svg)](https://github.com/iexbase/tron-api-python/issues)
[![Pull Requests](https://img.shields.io/github/issues-pr/iexbase/tron-api-python.svg)](https://github.com/iexbase/tron-api-python/pulls)
[![Contributors](https://img.shields.io/github/contributors/iexbase/tron-api-python.svg)](https://github.com/iexbase/tron-api-python/graphs/contributors)

## Install

| Setup   | Command             | Notes
| :------ | :------------------ | :---------
| install | `pip install tronapi`  |


## Basic Usage
Specify the API endpoints:

```python
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

**A full example:**

```python
from tronapi.provider import HttpProvider
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
> python cli.py send from to amount private_key
> python cli.py --generateaddress
> python cli.py --node=customnode --getbalance address
```


## Donations
**Tron(TRX)**: TRWBqiqoFZysoAeyR1J35ibuyc8EvhUAoY
