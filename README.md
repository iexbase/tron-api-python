# tron-api-python

## Install

```bash
> pip3 install tronapi
```

## Example Usage
```python
from tronapi.providers import HttpProvider
from tronapi.tron import Tron

full_node = HttpProvider('http://13.125.210.234:8090')
address = 'tron address'

tron = Tron(full_node)
tron.private_key = 'private_key'

print(tron.get_balance(address))
```
### cli
```bash
>>> python cli.py send from to amount private_key
>>> python cli.py --generateaddress
>>> python cli.py --node=customnode --getbalance address
