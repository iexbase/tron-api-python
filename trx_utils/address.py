
import base58

from typing import Any
from _sha256 import sha256
from trx_utils.hexadecimal import (
    is_hex,
    remove_0x_prefix
)
from trx_utils.types import (
    is_text,
    is_bytes
)


def is_hex_address(value: Any) -> bool:
    """
    Checks if the given string of text type is an address in hexadecimal encoded form.
    """
    if not is_text(value):
        return False
    elif not is_hex(value):
        return False
    else:
        un_prefixed = remove_0x_prefix(value)
        return len(un_prefixed) == 40


def is_binary_address(value: Any) -> bool:
    """
    Checks if the given string is an address in raw bytes form.
    """
    if not is_bytes(value):
        return False
    elif len(value) != 20:
        return False
    else:
        return True


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
