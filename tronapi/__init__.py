import pkg_resources

from tronapi.providers.http import HttpProvider  # noqa: E402
from tronapi.main import Tron  # noqa: E402

__version__ = pkg_resources.get_distribution("tronapi").version

__all__ = [
    '__version__',
    'HttpProvider',
    'Tron',
]
