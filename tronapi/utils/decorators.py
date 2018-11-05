import functools
import warnings


def deprecated_for(replace_message):
    """
    Decorate a deprecated function, with info about what to use instead, like:
    @deprecated_for("toBytes()")
    def toAscii(arg):
        ...
    """
    def decorator(to_wrap):
        @functools.wraps(to_wrap)
        def wrapper(*args, **kwargs):
            warnings.warn(
                "%s is deprecated in favor of %s" % (to_wrap.__name__, replace_message),
                category=DeprecationWarning,
                stacklevel=2)
            return to_wrap(*args, **kwargs)
        return wrapper
    return decorator
