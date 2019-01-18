import functools
import json

from eth_utils import (
    is_binary_address,
    to_hex,
    hexstr_if_str
)
from hexbytes import HexBytes
from toolz import curry

from tronapi.common.abi import process_type
from tronapi.common.account import Address
from tronapi.common.encoding import (
    to_bytes,
    text_if_str,
    to_text
)
from tronapi.common.validation import (
    validate_abi,
    validate_address
)


def implicitly_identity(to_wrap):
    @functools.wraps(to_wrap)
    def wrapper(abi_type, data):
        modified = to_wrap(abi_type, data)
        if modified is None:
            return abi_type, data
        else:
            return modified

    return wrapper


def normalize_abi(abi):
    if isinstance(abi, str):
        abi = json.loads(abi)
    validate_abi(abi)
    return abi


def normalize_bytecode(bytecode):
    if bytecode:
        bytecode = HexBytes(bytecode)
    return bytecode


@implicitly_identity
def abi_address_to_hex(abi_type, data):
    if abi_type == 'address':
        validate_address(data)
        if is_binary_address(data):
            return abi_type, to_hex(data)


@implicitly_identity
def abi_string_to_text(abi_type, data):
    if abi_type == 'string':
        return abi_type, text_if_str(to_text, data)


@implicitly_identity
def abi_bytes_to_bytes(abi_type, data):
    base, sub, arrlist = process_type(abi_type)
    if base == 'bytes' and not arrlist:
        return abi_type, hexstr_if_str(to_bytes, data)


@implicitly_identity
def addresses_checksummed(abi_type, data):
    if abi_type == 'address':
        return abi_type, to_checksum_address(data)


def to_checksum_address(address: str):
    return Address().from_hex(address)


@curry
def abi_resolver(abi_type, val):
    return abi_type, val


BASE_RETURN_NORMALIZERS = [
    addresses_checksummed,
]
