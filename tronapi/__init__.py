# --------------------------------------------------------------------------------------------
# Copyright (c) iEXBase. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import sys
import warnings

import pkg_resources

from tronapi.providers.http import HttpProvider  # noqa: E402
from tronapi.main import Tron  # noqa: E402

if (3, 5) <= sys.version_info < (3, 6):
    warnings.warn(
        "Support for Python 3.5 will be removed in tronapi v5",
        category=DeprecationWarning,
        stacklevel=2)

if sys.version_info < (3, 5):
    raise EnvironmentError(
        "Python 3.5 or above is required. "
        "Note that support for Python 3.5 will be remove in tronapi v5")


__version__ = pkg_resources.get_distribution("tronapi").version

__all__ = [
    '__version__',
    'HttpProvider',
    'Tron',
]