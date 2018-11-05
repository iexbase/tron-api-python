from _sha256 import sha256
from typing import Any

import base58
from eth_utils import is_hex_address

from tronapi.utils.hexadecimal import is_hex
from tronapi.utils.types import is_text


def string_utf8_to_hex(name):
    return bytes(name, encoding='utf-8').hex()
