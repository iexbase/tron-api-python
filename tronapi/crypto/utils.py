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


def is_integer(var):
    try:
        complex(var)
    except ValueError:
        return False

    return True
