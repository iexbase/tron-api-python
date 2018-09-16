from tron.tron import Tron

tron = Tron('https://api.trongrid.io:8090')
result = tron.get_transaction('TxId')
