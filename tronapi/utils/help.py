import re


def string_utf8_to_hex(name):
    return bytes(name, encoding='utf-8').hex()


def is_valid_url(value):
    """
    Return whether or not given value is a valid URL.

    :param value: URL address string to validate
    :param public: (default=False) Set True to only allow a public IP address
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
