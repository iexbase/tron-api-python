from eth_utils import (
    hexstr_if_str,
    to_bytes,
)


class HexBytes(bytes):
    '''
    This class is a *very* thin wrapper around the python
    built-in :class:`bytes` class. It has these three changes:
    1. Accepts hex strings as an initializing value
    2. Returns hex with prefix '0x' from :meth:`HexBytes.hex`
    3. The string representation at console is in hex
    '''
    def __new__(cls, val):
        bytesval = hexstr_if_str(to_bytes, val)
        return super().__new__(cls, bytesval)

    def hex(self):
        '''
        Just like :meth:`bytes.hex`, but prepends "0x"
        '''
        return '0x' + super().hex()

    def __repr__(self):
        return 'HexBytes(%r)' % self.hex()