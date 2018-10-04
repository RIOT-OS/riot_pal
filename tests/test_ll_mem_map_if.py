"""Tests all functions supported functions."""
from pprint import pformat
from pathlib import Path
from serial import SerialException
from riot_pal import LLMemMapIf
import helpers


def try_connect(mem_map='mem_map.csv'):
    try:
        return LLMemMapIf(mem_map, 'serial', '/dev/ttyACM0', timeout=1)
    except SerialException:
        return LLMemMapIf(mem_map, 'serial', '/dev/ttyUSB0', timeout=1)


def test_philip_mem_map_basic(regtest):
    mmif = try_connect(str(Path(__file__).parents[1]) + '/mem_map/philip_mem_map.csv')
    regtest.write(pformat(mmif.cmd_list) + '\n')
    regtest.write(pformat(mmif.reset_mcu()) + '\n')
    regtest.write(pformat(mmif.execute_changes()) + '\n')
    mmif.close()


def test_philip_mem_map_read_reg(regtest):
    mmif = try_connect(str(Path(__file__).parents[1]) + '/mem_map/philip_mem_map.csv')
    regtest.write(pformat(mmif.reset_mcu()) + '\n')

    for cmd in sorted(mmif.cmd_list):
        # Supress unused variable warning
        cmd_vals = mmif.cmd_list[cmd]
        read_val = mmif.read_reg(cmd)
        if 'DEVICE_SPECIFIC' in cmd_vals['flag']:
            read_val.pop('data', None)
        elif cmd_vals['default'] is not '':
            assert helpers.weak_cmp(read_val['data'], cmd_vals['default'])
        regtest.write(pformat(read_val) + '\n')
    mmif.close()


def test_philip_mem_map_write_reg(regtest):
    mmif = try_connect(str(Path(__file__).parents[1]) + '/mem_map/philip_mem_map.csv')
    regtest.write(pformat(mmif.reset_mcu()) + '\n')

    for cmd in sorted(mmif.cmd_list):
        # Supress unused variable warning
        read_val = mmif.read_reg(cmd)
        write_ret = mmif.write_reg(cmd, helpers.try_add(read_val['data']))
        read_val = mmif.read_reg(cmd)
        regtest.write(pformat(write_ret) + '\n')
        regtest.write(pformat(read_val) + '\n')
    mmif.close()
