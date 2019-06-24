# Copyright (c) 2018 Kevin Weiss, for HAW Hamburg  <kevin.weiss@haw-hamburg.de>
#
# This file is subject to the terms and conditions of the MIT License. See the
# file LICENSE in the top level directory for more details.
# SPDX-License-Identifier:    MIT
"""packet init for RIOT PAL
This exposes usful modules in the RIOT PAL packet
"""
from .dut_shell import DutShell

__all__ = ['DutShell']
