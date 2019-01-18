# --------------------------------------------------------------------
# Copyright (c) iEXBase. All rights reserved.
# Licensed under the MIT License.
# See License.txt in the project root for license information.
# --------------------------------------------------------------------

try:
    from cytoolz import (
        assoc,
        complement,
        compose,
        concat,
        curry,
        dicttoolz,
        dissoc,
        excepts,
        functoolz,
        groupby,
        identity,
        itertoolz,
        merge,
        partial,
        pipe,
        sliding_window,
        valfilter,
        valmap,
    )
except ImportError:
    from toolz import (  # noqa: F401
        assoc,
        complement,
        compose,
        concat,
        curry,
        dicttoolz,
        dissoc,
        excepts,
        functoolz,
        groupby,
        identity,
        itertoolz,
        merge,
        partial,
        pipe,
        sliding_window,
        valfilter,
        valmap,
    )
