from tronapi.tron import Tron

tron = Tron('https://api.trongrid.io:8090')

tron.to_hex('TT67rPNwgmpeimvHUMVzFfKsjL9GZ1wGw8')
# result: 41BBC8C05F1B09839E72DB044A6AA57E2A5D414A10

tron.from_hex('41BBC8C05F1B09839E72DB044A6AA57E2A5D414A10')
# result: TT67rPNwgmpeimvHUMVzFfKsjL9GZ1wGw8
