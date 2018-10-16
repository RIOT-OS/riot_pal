# Copyright (c) 2018 Kevin Weiss, for HAW Hamburg  <kevin.weiss@haw-hamburg.de>
#
# This file is subject to the terms and conditions of the MIT License. See the
# file LICENSE in the top level directory for more details.
# SPDX-License-Identifier:    MIT
"""Tests Serial Driver implmentation in RIOT PAL."""
from pprint import pformat
from serial import SerialException
from riot_pal.serial_driver import SerialDriver

WORKING_PORT = '/dev/ttyACM0'
WORKING_BAUD = 115200
FAILING_PORT = 'ERROR'
FAILING_BAUD = 19200


def _open_write_read_close(regtest, *args, **kwrgs):
    regtest.write('Opening with args:\n')
    regtest.write(pformat(args) + '\n')
    regtest.write(pformat(kwrgs) + '\n')
    try:
        ser_drvr = SerialDriver(*args, **kwrgs)
        ser_drvr.write('')
        regtest.write(ser_drvr.read())
        ser_drvr.close()
        regtest.write('SUCCESS\n')
    except (SerialException, TypeError) as exc:
        regtest.write(str(exc) + '\n')


def test_connect_working(regtest):
    """Test working serial connections."""
    test_port = WORKING_PORT
    test_baud = WORKING_BAUD
    _open_write_read_close(regtest)
    _open_write_read_close(regtest, test_port)
    _open_write_read_close(regtest,
                           port=test_port)
    _open_write_read_close(regtest,
                           test_port,
                           test_baud)
    _open_write_read_close(regtest,
                           test_port,
                           baudrate=test_baud)
    _open_write_read_close(regtest,
                           baudrate=test_baud,
                           port=test_port,
                           timeout=2)


def test_connect_failing(regtest):
    """Test failing serial connections."""
    test_port = FAILING_PORT
    test_baud = FAILING_BAUD
    _open_write_read_close(regtest, test_port)
    _open_write_read_close(regtest,
                           port=test_port)
    _open_write_read_close(regtest,
                           test_port,
                           test_baud)
    _open_write_read_close(regtest,
                           test_port,
                           baudrate=test_baud)
    _open_write_read_close(regtest,
                           baudrate=test_baud,
                           port=test_port,
                           timeout=2)
