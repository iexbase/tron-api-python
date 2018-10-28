import string


def is_numeric(x) -> bool:
    return isinstance(x, int)


def is_string(x) -> bool:
    return isinstance(x, str)


def is_hex(s):
    hex_digits = set(string.hexdigits)
    return all(c in hex_digits for c in s)
