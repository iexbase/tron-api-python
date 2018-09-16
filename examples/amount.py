from tron.tron import Tron

tron = Tron('https://api.trongrid.io:8090')


tron.to_tron(1)
# result: 1000000

tron.from_tron(1000000)
# result: 1


