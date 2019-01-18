# --------------------------------------------------------------------
# Copyright (c) iEXBase. All rights reserved.
# Licensed under the MIT License.
# See License.txt in the project root for license information.
# --------------------------------------------------------------------
import platform
from typing import Any

import base58
import tronapi


def format_user_agent(name=None):
    """Construct a User-Agent suitable for use in client code.
    This will identify use by the provided ``name`` (which should be on the
    format ``dist_name/version``), TronAPI version and Python version.
    .. versionadded:: 1.1
    """
    parts = ['TronAPI/%s' % tronapi.__version__,
             '%s/%s' % (platform.python_implementation(),
                        platform.python_version())]
    if name:
        parts.insert(0, name)
    return ' '.join(parts)


def string_utf8_to_hex(name):
    return bytes(name, encoding='utf-8').hex()


def hex_to_base58(value: Any) -> str:
    return base58.b58encode_check(bytes.fromhex(value))
