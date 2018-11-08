from _sha256 import sha256
from typing import Any

import base58

from tronapi.utils.hexadecimal import is_hex
from tronapi.utils.types import is_text


def is_address(value: str) -> bool:
    """Checks if the given string in a supported value is an address
    in any of the known formats.

    Args:
        value (str): Address

    """
    if is_checksum_address(value):
        return True
    elif is_hex_address(value):
        return True

    return False


def is_hex_address(value: Any) -> bool:
    """Checks if the given string of text type is an address in hexadecimal encoded form."""
    if len(value) != 42:
        return False
    elif not is_text(value):
        return False
    elif not is_hex(value):
        return False
    else:
        return is_address(
            hex_to_base58(value)
        )


def is_checksum_address(value: str) -> bool:
    if len(value) != 34:
        return False

    address = base58.b58decode(value)
    if len(address) != 25:
        return False

    if address[0] != 0x41:
        return False

    check_sum = sha256(sha256(address[:-4]).digest()).digest()[:4]
    if address[-4:] == check_sum:
        return True


def hex_to_base58(value: Any) -> str:
    return base58.b58encode_check(bytes.fromhex(value))
