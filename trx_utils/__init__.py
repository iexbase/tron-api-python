# --------------------------------------------------------------------
# Copyright (c) iEXBase. All rights reserved.
# Licensed under the MIT License.
# See License.txt in the project root for license information.
# --------------------------------------------------------------------

import pkg_resources
import sys
import warnings

from .address import (  # noqa: F401
    is_address,
    is_binary_address,
    is_checksum_address,
    is_hex_address
)

from .currency import (  # noqa: F401
    from_sun,
    to_sun
)

from .decorators import (  # noqa: F401
    combomethod,
    reject_recursive_repeats,
    deprecated_for
)

from .hexadecimal import (  # noqa: F401
    add_0x_prefix,
    decode_hex,
    encode_hex,
    is_0x_prefixed,
    is_hex,
    remove_0x_prefix,
)

from .types import (  # noqa: F401
    is_boolean,
    is_bytes,
    is_dict,
    is_integer,
    is_list,
    is_list_like,
    is_null,
    is_number,
    is_string,
    is_text,
    is_tuple,
)


if sys.version_info.major < 3:
    warnings.simplefilter("always", DeprecationWarning)
    warnings.warn(
        DeprecationWarning(
            "The `trx-utils` library has dropped support for Python 2. Upgrade to Python 3."
        )
    )
    warnings.resetwarnings()


__version__ = pkg_resources.get_distribution("trx-utils").version
