import string


def is_bool(x) -> bool:
    return isinstance(x, bool)


def is_numeric(x) -> bool:
    return isinstance(x, int)


def is_string(x) -> bool:
    return isinstance(x, str)


def is_object(x) -> bool:
    return isinstance(x, object)


def is_hex(s):
    hex_digits = set(string.hexdigits)
    return all(c in hex_digits for c in s)


def string_utf8_to_hex(name):
    return bytes(name, encoding='utf-8').hex()