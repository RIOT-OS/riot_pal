# Copyright (c) 2018 Kevin Weiss, for HAW Hamburg  <kevin.weiss@haw-hamburg.de>
#
# This file is subject to the terms and conditions of the MIT License. See the
# file LICENSE in the top level directory for more details.
# SPDX-License-Identifier:    MIT
"""Helper functions for running tests on RIOT PAL."""

def _try_parse_int(val):
    try:
        return int(val, 0)
    except (ValueError, TypeError):
        return val


def weak_cmp(val1, val2):
    """Compares write numbers that ban be hex, string, or int.

    Args:
        val1(int, str): Value to compare.
        val2(int, str): Value to compare.

    Return:
        bool: True if aproximatly equal, False if not.
    """
    return _try_parse_int(val1) == _try_parse_int(val2)


def try_add(val):
    """Attempts to add a number to a value.

    Args:
        val(int, str, list): Value to add the number to.

    Return:
        int: If successful returns the val + 1.  If failed just retruns the val.
    """
    try:
        return _try_parse_int(val)+1
    except TypeError:
        try:
            val[0] = _try_parse_int(val[0])+1
            return val
        except TypeError:
            return val
