# --------------------------------------------------------------------------------------------
# Copyright (c) iEXBase. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from trx_utils import (
    is_string,
    remove_0x_prefix,
    is_hex,
    is_integer
)


def is_hex_encoded_block_hash(value):
    if not is_string(value):
        return False
    return len(remove_0x_prefix(value)) == 64 and is_hex(value)


def is_hex_encoded_block_number(value):
    if not is_string(value):
        return False
    elif is_hex_encoded_block_hash(value):
        return False
    try:
        value_as_int = int(value, 16)
    except ValueError:
        return False
    return 0 <= value_as_int < 2**256


def select_method_for_block(value, if_hash, if_number):
    if isinstance(value, bytes):
        return if_hash
    elif is_hex_encoded_block_hash(value):
        return if_hash
    elif is_integer(value) and (0 <= value < 2**256):
        return if_number
    elif is_hex_encoded_block_number(value):
        return if_number
    else:
        raise ValueError(
            "Value did not match any of the recognized block identifiers: {0}".format(value)
        )
