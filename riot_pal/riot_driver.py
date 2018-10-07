# Copyright (c) 2018 Kevin Weiss, for HAW Hamburg  <kevin.weiss@haw-hamburg.de>
#
# This file is subject to the terms and conditions of the MIT License. See the
# file LICENSE in the top level directory for more details.
# SPDX-License-Identifier:    MIT
"""RIOT Driver for RIOT PAL
This module handles generic connection and IO to the make term.
"""


class RiotDriver:
    """Contains all reusable functions for connecting, sending and recieveing
    data.

    """

    def __init__(self):
        raise NotImplementedError()

    def close(self):
        """Close serial connection."""
        raise NotImplementedError()

    def read(self):
        """Read and decode data."""
        raise NotImplementedError()

    def write(self, data):
        """Tries write data."""
        raise NotImplementedError()
