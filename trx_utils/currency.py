# --------------------------------------------------------------------
# Copyright (c) iEXBase. All rights reserved.
# Licensed under the MIT License.
# See License.txt in the project root for license information.
# --------------------------------------------------------------------

import decimal
from decimal import localcontext
from typing import Union

from trx_utils.types import (
    is_string,
    is_integer
)

MIN_SUN = 0
MAX_SUN = 2 ** 256 - 1
UNITS = {
    'sun': decimal.Decimal('1000000')
}


def from_sun(number: int) -> Union[int, decimal.Decimal]:
    """Helper function that will convert a value in SUN to TRX.

    Args:
        number (int): Value in SUN to convert to TRX

    """
    if number == 0:
        return 0

    if number < MIN_SUN or number > MAX_SUN:
        raise ValueError("value must be between 1 and 2**256 - 1")

    unit_value = UNITS['sun']

    with localcontext() as ctx:
        ctx.prec = 999
        d_number = decimal.Decimal(value=number, context=ctx)
        result_value = d_number / unit_value

    return result_value


def to_sun(number: int) -> int:
    """Helper function that will convert a value in TRX to SUN.

    Args:
        number (int): Value in TRX to convert to SUN

    """
    if is_integer(number) or is_string(number):
        d_number = decimal.Decimal(value=number)
    elif isinstance(number, float):
        d_number = decimal.Decimal(value=str(number))
    elif isinstance(number, decimal.Decimal):
        d_number = number
    else:
        raise TypeError("Unsupported type.  Must be one of integer, float, or string")

    s_number = str(number)
    unit_value = UNITS['sun']

    if d_number == 0:
        return 0

    if d_number < 1 and '.' in s_number:
        with localcontext() as ctx:
            multiplier = len(s_number) - s_number.index('.') - 1
            ctx.prec = multiplier
            d_number = decimal.Decimal(value=number, context=ctx) * 10 ** multiplier
        unit_value /= 10 ** multiplier

    with localcontext() as ctx:
        ctx.prec = 999
        result_value = decimal.Decimal(value=d_number, context=ctx) * unit_value

    if result_value < MIN_SUN or result_value > MAX_SUN:
        raise ValueError("Resulting wei value must be between 1 and 2**256 - 1")

    return int(result_value)
