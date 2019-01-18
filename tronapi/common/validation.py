# --------------------------------------------------------------------------------------------
# Copyright (c) iEXBase. All rights reserved.
# Licensed under the MIT License.
# See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import itertools
import re
from _sha256 import sha256
from typing import Any

import base58
from eth_utils import (
    function_abi_to_4byte_selector,
    apply_formatter_to_array
)

from trx_utils import (
    is_hex,
    encode_hex,
    is_0x_prefixed,
    is_text,
    is_list_like,
    is_dict,
    is_string,
    is_bytes,
    is_boolean,
    is_integer,
    is_binary_address, is_hex_address, is_checksum_address)

from tronapi.common.toolz import (
    compose,
    groupby,
    valfilter,
    valmap,
)

from tronapi.common.abi import filter_by_type, abi_to_signature, is_recognized_type, is_string_type, is_bytes_type, \
    is_address_type, is_int_type, is_uint_type, is_bool_type, sub_type_of_array_type, is_array_type, \
    length_of_array_type
from tronapi.exceptions import InvalidAddress


def _prepare_selector_collision_msg(duplicates):
    dup_sel = valmap(apply_formatter_to_array(abi_to_signature), duplicates)
    joined_funcs = valmap(lambda f: ', '.join(f), dup_sel)
    func_sel_msg_list = [funcs + ' have selector ' + sel for sel, funcs in joined_funcs.items()]
    return ' and\n'.join(func_sel_msg_list)


def is_valid_url(value):
    """Return whether or not given value is a valid URL.

    Args:
        value(str): URL address string to validate
    """
    regex = re.compile(
        r'^(?:http|ftp)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    result = regex.match(value)
    return bool(result)


def validate_abi(abi):
    """
    Helper function for validating an ABI
    """
    if not is_list_like(abi):
        raise ValueError("'abi' is not a list")

    if not all(is_dict(e) for e in abi):
        raise ValueError("'abi' is not a list of dictionaries")

    functions = filter_by_type('function', abi)
    selectors = groupby(
        compose(encode_hex, function_abi_to_4byte_selector),
        functions
    )
    duplicates = valfilter(lambda funcs: len(funcs) > 1, selectors)
    if duplicates:
        raise ValueError(
            'Abi contains functions with colliding selectors. '
            'Functions {0}'.format(_prepare_selector_collision_msg(duplicates))
        )


def validate_abi_type(abi_type):
    """
    Helper function for validating an abi_type
    """
    if not is_recognized_type(abi_type):
        raise ValueError("Unrecognized abi_type: {abi_type}".format(abi_type=abi_type))


def validate_abi_value(abi_type, value):
    """
    Helper function for validating a value against the expected abi_type
    Note: abi_type 'bytes' must either be python3 'bytes' object or ''
    """
    if is_array_type(abi_type) and is_list_like(value):
        # validate length
        specified_length = length_of_array_type(abi_type)
        if specified_length is not None:
            if specified_length < 1:
                raise TypeError(
                    "Invalid abi-type: {abi_type}. Length of fixed sized arrays"
                    "must be greater than 0."
                        .format(abi_type=abi_type)
                )
            if specified_length != len(value):
                raise TypeError(
                    "The following array length does not the length specified"
                    "by the abi-type, {abi_type}: {value}"
                        .format(abi_type=abi_type, value=value)
                )

        # validate sub_types
        sub_type = sub_type_of_array_type(abi_type)
        for v in value:
            validate_abi_value(sub_type, v)
        return
    elif is_bool_type(abi_type) and is_boolean(value):
        return
    elif is_uint_type(abi_type) and is_integer(value) and value >= 0:
        return
    elif is_int_type(abi_type) and is_integer(value):
        return
    elif is_address_type(abi_type):
        validate_address(value)
        return
    elif is_bytes_type(abi_type):
        if is_bytes(value):
            return
        elif is_string(value):
            if is_0x_prefixed(value):
                return
            else:
                raise TypeError(
                    "ABI values of abi-type 'bytes' must be either"
                    "a python3 'bytes' object or an '0x' prefixed string."
                )
    elif is_string_type(abi_type) and is_string(value):
        return

    raise TypeError(
        "The following abi value is not a '{abi_type}': {value}".format(abi_type=abi_type, value=value)
    )


def validate_address(value):
    """
    Helper function for validating an address
    """
    if is_bytes(value):
        if not is_binary_address(value):
            raise InvalidAddress("Address must be 20 bytes when input type is bytes", value)
        return

    if not isinstance(value, str):
        raise TypeError('Address {} must be provided as a string'.format(value))
    if not is_hex_address(value):
        raise InvalidAddress("Address must be 20 bytes, as a hex string with a 0x prefix", value)
    if not is_checksum_address(value):
        if value == value.lower():
            raise InvalidAddress(
                "Web3.py only accepts checksum addresses. "
                "The software that gave you this non-checksum address should be considered unsafe, "
                "please file it as a bug on their platform. "
                "Try using an ENS name instead. Or, if you must accept lower safety, "
                "use Web3.toChecksumAddress(lower_case_address).",
                value,
            )
        else:
            raise InvalidAddress(
                "Address has an invalid EIP-55 checksum. "
                "After looking up the address from the original source, try again.",
                value,
            )


def has_one_val(*args, **kwargs):
    vals = itertools.chain(args, kwargs.values())
    not_nones = list(filter(lambda val: val is not None, vals))
    return len(not_nones) == 1


def assert_one_val(*args, **kwargs):
    if not has_one_val(*args, **kwargs):
        raise TypeError(
            "Exactly one of the passed values can be specified. "
            "Instead, values were: %r, %r" % (args, kwargs)
        )
