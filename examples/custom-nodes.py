from tronapi.providers import HttpProvider
from tronapi.tron import Tron

# Recommend FullNode: http://13.125.210.234:8090


fullNode = HttpProvider('https://api.trongrid.io:8090')

# Example 1
tron_1 = Tron(fullNode)

# Example 2
tron_2 = Tron('https://api.trongrid.io:8090')
