from tronapi.tron import Tron

tron = Tron('https://api.trongrid.io:8090')
tron.private_key = 'private_key'

result = tron.send_transaction('FromAddress', 'ToAddress', 1)

# Получаем результат
print(result)
