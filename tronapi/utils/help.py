import re
from typing import Any

import base58


def string_utf8_to_hex(name):
    return bytes(name, encoding='utf-8').hex()


def hex_to_base58(value: Any) -> str:
    return base58.b58encode_check(bytes.fromhex(value))


def construct_user_agent():
    from tronapi import __version__ as tron_version
    user_agent = 'TronAPI/{version}'.format(
        version=tron_version
    )
    return user_agent


def is_valid_url(value):
    """
    Return whether or not given value is a valid URL.

    :param value: URL address string to validate
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
