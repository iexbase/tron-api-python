import json
import re
from typing import Union

from tronapi.common.datastructures import AttributeDict
from hexbytes import HexBytes

from eth_utils import (
    hexstr_if_str,
    to_hex,
    big_endian_to_int,
    int_to_big_endian
)
from trx_utils import (
    remove_0x_prefix,
    encode_hex,
    add_0x_prefix,
    decode_hex,
    is_boolean,
    is_integer,
    is_list_like,
    is_bytes
)

from tronapi.common.abi import (
    size_of_type,
    sub_type_of_array_type,
    is_array_type,
    is_bool_type,
    is_uint_type,
    is_int_type,
    is_address_type,
    is_bytes_type,
    is_string_type
)


from tronapi.common.validation import (
    validate_abi_type,
    validate_abi_value
)

from tronapi.common.toolz import (
    curry
)

from tronapi.common.validation import assert_one_val


def hex_encode_abi_type(abi_type, value, force_size=None):
    """
    Encodes value into a hex string in format of abi_type
    """
    validate_abi_type(abi_type)
    validate_abi_value(abi_type, value)

    data_size = force_size or size_of_type(abi_type)
    if is_array_type(abi_type):
        sub_type = sub_type_of_array_type(abi_type)
        return "".join([remove_0x_prefix(hex_encode_abi_type(sub_type, v, 256)) for v in value])
    elif is_bool_type(abi_type):
        return to_hex_with_size(value, data_size)
    elif is_uint_type(abi_type):
        return to_hex_with_size(value, data_size)
    elif is_int_type(abi_type):
        return to_hex_twos_compliment(value, data_size)
    elif is_address_type(abi_type):
        return pad_hex(value, data_size)
    elif is_bytes_type(abi_type):
        if is_bytes(value):
            return encode_hex(value)
        else:
            return value
    elif is_string_type(abi_type):
        return to_hex(text=value)
    else:
        raise ValueError(
            "Unsupported ABI type: {0}".format(abi_type)
        )


def to_hex_twos_compliment(value, bit_size):
    """
    Converts integer value to twos compliment hex representation with given bit_size
    """
    if value >= 0:
        return to_hex_with_size(value, bit_size)

    value = (1 << bit_size) + value
    hex_value = hex(value)
    hex_value = hex_value.rstrip("L")
    return hex_value


def to_hex_with_size(value, bit_size):
    """Converts a value to hex with given bit_size:"""
    return pad_hex(to_hex(value), bit_size)


def pad_hex(value, bit_size):
    """Pads a hex string up to the given bit_size"""
    value = remove_0x_prefix(value)
    return add_0x_prefix(value.zfill(int(bit_size / 4)))


def trim_hex(hexstr):
    if hexstr.startswith('0x0'):
        hexstr = re.sub('^0x0+', '0x', hexstr)
        if hexstr == '0x':
            hexstr = '0x0'
    return hexstr


def to_int(value=None, hexstr=None, text=None):
    """Converts value to it's integer representation.

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


@curry
def text_if_str(to_type, text_or_primitive):
    """Convert to a type, assuming that strings can be only unicode text (not a hexstr)"""
    if isinstance(text_or_primitive, str):
        (primitive, text) = (None, text_or_primitive)
    else:
        (primitive, text) = (text_or_primitive, None)
    return to_type(primitive, text=text)


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


def to_4byte_hex(hex_or_str_or_bytes: Union[int, str, bytes]) -> str:
    size_of_4bytes = 4 * 8
    byte_str = hexstr_if_str(to_bytes, hex_or_str_or_bytes)
    if len(byte_str) > 4:
        raise ValueError(
            'expected value of size 4 bytes. Got: %d bytes' % len(byte_str)
        )
    hex_str = encode_hex(byte_str)
    return pad_hex(hex_str, size_of_4bytes)


class FriendlyJsonSerialize:
    """
    Friendly JSON serializer & deserializer
    When encoding or decoding fails, this class collects
    information on which fields failed, to show more
    helpful information in the raised error messages.
    """

    def _json_mapping_errors(self, mapping):
        for key, val in mapping.items():
            try:
                self._friendly_json_encode(val)
            except TypeError as exc:
                yield "%r: because (%s)" % (key, exc)

    def _json_list_errors(self, iterable):
        for index, element in enumerate(iterable):
            try:
                self._friendly_json_encode(element)
            except TypeError as exc:
                yield "%d: because (%s)" % (index, exc)

    def _friendly_json_encode(self, obj, cls=None):
        try:
            encoded = json.dumps(obj, cls=cls)
            return encoded
        except TypeError as full_exception:
            if hasattr(obj, 'items'):
                item_errors = '; '.join(self._json_mapping_errors(obj))
                raise TypeError("dict had unencodable value at keys: {{{}}}".format(item_errors))
            elif is_list_like(obj):
                element_errors = '; '.join(self._json_list_errors(obj))
                raise TypeError("list had unencodable value at index: [{}]".format(element_errors))
            else:
                raise full_exception

    @staticmethod
    def json_decode(json_str):
        try:
            decoded = json.loads(json_str)
            return decoded
        except json.decoder.JSONDecodeError as exc:
            err_msg = 'Could not decode {} because of {}.'.format(repr(json_str), exc)
            # Calling code may rely on catching JSONDecodeError to recognize bad json
            # so we have to re-raise the same type.
            raise json.decoder.JSONDecodeError(err_msg, exc.doc, exc.pos)

    def json_encode(self, obj, cls=None):
        try:
            return self._friendly_json_encode(obj, cls=cls)
        except TypeError as exc:
            raise TypeError("Could not encode to JSON: {}".format(exc))


class TronJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, AttributeDict):
            return {k: v for k, v in obj.items()}
        if isinstance(obj, HexBytes):
            return obj.hex()
        return json.JSONEncoder.default(self, obj)


def to_json(obj: object) -> object:
    """Convert a complex object (like a transaction object) to a JSON string"""
    return FriendlyJsonSerialize().json_encode(obj, cls=TronJsonEncoder)
