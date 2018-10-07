# Copyright (c) 2018 Kevin Weiss, for HAW Hamburg  <kevin.weiss@haw-hamburg.de>
#
# This file is subject to the terms and conditions of the MIT License. See the
# file LICENSE in the top level directory for more details.
# SPDX-License-Identifier:    MIT
"""Helper functions for running tests on RIOT PAL."""


def weak_cmp(val1, val2):
    return try_parse_int(val1) == try_parse_int(val2)


def try_add(val):
    try:
        return try_parse_int(val)+1
    except TypeError:
        return val


def try_parse_int(val):
    try:
        return int(val, 0)
    except (ValueError, TypeError):
        return val
