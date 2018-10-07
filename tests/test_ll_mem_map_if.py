# Copyright (c) 2018 Kevin Weiss, for HAW Hamburg  <kevin.weiss@haw-hamburg.de>
#
# This file is subject to the terms and conditions of the MIT License. See the
# file LICENSE in the top level directory for more details.
# SPDX-License-Identifier:    MIT
"""Tests all commands imported by mem_map file."""
from pprint import pformat
from serial import SerialException
from riot_pal import LLMemMapIf
from riot_pal import PHILIP_MEM_MAP_PATH
import helpers


def try_connect(mem_map='mem_map.csv'):
    try:
        return LLMemMapIf(mem_map, 'serial', '/dev/ttyACM0', timeout=1)
    except SerialException:
        return LLMemMapIf(mem_map, 'serial', '/dev/ttyUSB0', timeout=1)


def test_philip_mem_map_basic(regtest):
    mmif = try_connect(PHILIP_MEM_MAP_PATH)
    regtest.write(pformat(mmif.cmd_list) + '\n')
    regtest.write(pformat(mmif.reset_mcu()) + '\n')
    regtest.write(pformat(mmif.execute_changes()) + '\n')
    mmif.close()


def test_philip_mem_map_read_reg(regtest):
    mmif = try_connect(PHILIP_MEM_MAP_PATH)
    regtest.write(pformat(mmif.reset_mcu()) + '\n')

    for cmd in sorted(mmif.cmd_list):
        cmd_vals = mmif.cmd_list[cmd]
        read_val = mmif.read_reg(cmd)
        if 'DEVICE_SPECIFIC' in cmd_vals['flag']:
            read_val.pop('data', None)
        elif cmd_vals['default'] is not '':
            assert helpers.weak_cmp(read_val['data'], cmd_vals['default'])
        regtest.write(pformat(read_val) + '\n')
    mmif.close()


def test_philip_mem_map_write_reg(regtest):
    mmif = try_connect(PHILIP_MEM_MAP_PATH)
    regtest.write(pformat(mmif.reset_mcu()) + '\n')

    for cmd in sorted(mmif.cmd_list):
        read_val = mmif.read_reg(cmd)
        write_ret = mmif.write_reg(cmd, helpers.try_add(read_val['data']))
        read_val = mmif.read_reg(cmd)
        regtest.write(pformat(write_ret) + '\n')
        regtest.write(pformat(read_val) + '\n')
    mmif.close()
