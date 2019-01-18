# --------------------------------------------------------------------
# Copyright (c) iEXBase. All rights reserved.
# Licensed under the MIT License.
# See License.txt in the project root for license information.
# --------------------------------------------------------------------

from collections import Mapping, Iterable

from eth_utils import to_dict
from trx_utils import (
    reject_recursive_repeats,
    is_string
)

from tronapi.common.toolz import (
    curry
)


@curry
@to_dict
def apply_formatters_to_dict(formatters, value):
    for key, item in value.items():
        if key in formatters:
            try:
                yield key, formatters[key](item)
            except (TypeError, ValueError) as exc:
                raise type(exc)("Could not format value %r as field %r" % (item, key)) from exc
        else:
            yield key, item


@reject_recursive_repeats
def recursive_map(func, data):
    """
    Apply func to data, and any collection items inside data (using map_collection).
    Define func so that it only applies to the type of value that you want it to apply to.
    """

    def recurse(item):
        return recursive_map(func, item)

    items_mapped = map_collection(recurse, data)
    return func(items_mapped)


def map_collection(func, collection):
    """
    Apply func to each element of a collection, or value of a dictionary.
    If the value is not a collection, return it unmodified
    """
    datatype = type(collection)
    if isinstance(collection, Mapping):
        return datatype((key, func(val)) for key, val in collection.items())
    if is_string(collection):
        return collection
    elif isinstance(collection, Iterable):
        return datatype(map(func, collection))
    else:
        return collection
