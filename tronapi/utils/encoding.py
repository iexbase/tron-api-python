# --------------------------------------------------------------------------------------------
# Copyright (c) iEXBase. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from eth_utils import big_endian_to_int, int_to_big_endian, to_hex
from tronapi.utils.hexadecimal import remove_0x_prefix, decode_hex
from tronapi.utils.types import is_integer, is_boolean
from tronapi.utils.validation import assert_one_val


def to_int(value=None, hexstr=None, text=None):
    """
    Converts value to it's integer representation.

    Values are converted this way:

     * value:
       * bytes: big-endian integer
       * bool: True => 1, False => 0
     * hexstr: interpret hex as integer
     * text: interpret as string of digits, like '12' => 12
    """
    assert_one_val(value, hexstr=hexstr, text=text)

    if hexstr is not None:
        return int(hexstr, 16)
    elif text is not None:
        return int(text)
    elif isinstance(value, bytes):
        return big_endian_to_int(value)
    elif isinstance(value, str):
        raise TypeError("Pass in strings with keyword hexstr or text")
    else:
        return int(value)


def to_bytes(primitive=None, hexstr=None, text=None):
    assert_one_val(primitive, hexstr=hexstr, text=text)

    if is_boolean(primitive):
        return b'\x01' if primitive else b'\x00'
    elif isinstance(primitive, bytes):
        return primitive
    elif is_integer(primitive):
        return to_bytes(hexstr=to_hex(primitive))
    elif hexstr is not None:
        if len(hexstr) % 2:
            hexstr = '0x0' + remove_0x_prefix(hexstr)
        return decode_hex(hexstr)
    elif text is not None:
        return text.encode('utf-8')
    raise TypeError("expected an int in first arg, or keyword of hexstr or text")


def to_text(primitive=None, hexstr=None, text=None):
    assert_one_val(primitive, hexstr=hexstr, text=text)

    if hexstr is not None:
        return to_bytes(hexstr=hexstr).decode('utf-8')
    elif text is not None:
        return text
    elif isinstance(primitive, str):
        return to_text(hexstr=primitive)
    elif isinstance(primitive, bytes):
        return primitive.decode('utf-8')
    elif is_integer(primitive):
        byte_encoding = int_to_big_endian(primitive)
        return to_text(byte_encoding)
    raise TypeError("Expected an int, bytes or hexstr.")
