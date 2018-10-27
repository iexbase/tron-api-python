import sys


def compat_bytes(item, encoding=None):
    """Этот метод требуется, потому что Python 2.7 `bytes`
    является просто псевдонимом для` str`. Без этого метода,

    :param item:
    :param encoding:
    :return:
    """
    if hasattr(item, '__bytes__'):
        return item.__bytes__()
    else:
        if encoding:
            return bytes(item, encoding)
        else:
            return bytes(item)


def is_numeric(x):
    return isinstance(x, int)


def is_string(x):
    return isinstance(x, bytes)
