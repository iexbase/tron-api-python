from tron.tron import Tron

tron = Tron('https://api.trongrid.io:8090')

result = tron.send_transaction('FromAddress', 'ToAddress', 1)

# Получаем результат
print(result)
