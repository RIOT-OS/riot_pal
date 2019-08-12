# Copyright (c) 2018 Kevin Weiss, for HAW Hamburg  <kevin.weiss@haw-hamburg.de>
#
# This file is subject to the terms and conditions of the MIT License. See the
# file LICENSE in the top level directory for more details.
# SPDX-License-Identifier:    MIT
"""Serial Driver for RIOT PAL
This module handles generic connection and IO to the serial driver.
"""
import logging
import time
from serial import Serial, serial_for_url, SerialException


class SerialDriver:
    """Contains all reusable functions for connecting, sending and receiving
    data.  Arguments are passed through to the standard pyserial driver.  The
    defaults are changed.  Also if env variables are defined they get used as
    defaults.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
    """
    DEFAULT_TIMEOUT = 1
    DEFAULT_BAUDRATE = 115200
    DEFAULT_PORT = '/dev/ttyACM0'
    DEFAULT_CONNECT_WAIT = 0

    def __init__(self, *args, **kwargs):
        self._connect(*args, **kwargs)

    def _connect(self, *args, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = SerialDriver.DEFAULT_TIMEOUT
        if len(args) < 2:
            if 'baudrate' not in kwargs:
                kwargs['baudrate'] = SerialDriver.DEFAULT_BAUDRATE
        if len(args) == 0:
            if 'port' not in kwargs:
                kwargs['port'] = SerialDriver.DEFAULT_PORT

        connect_wait = kwargs.pop('connect_wait', self.DEFAULT_CONNECT_WAIT)
        logging.debug("Serial connection args %r -- %r", args, kwargs)
        try:
            self._dev = Serial(*args, **kwargs)
        except SerialException:
            self._dev = serial_for_url(*args, **kwargs)
        time.sleep(int(connect_wait))
        kwargs['connect_wait'] = connect_wait
        self.args = args
        self.kwargs = kwargs

    def close(self):
        """Close serial connection."""
        logging.debug("Closing %s", self._dev.port)
        self._dev.close()

    def readline(self):
        """Read and decode to utf-8 data.

        Returns:
            str: string of data if success, empty string if failed.
        """
        try:
            res_bytes = self._dev.readline()
            response = res_bytes.decode("utf-8", errors="ignore")
        except (ValueError, TypeError, SerialException) as exc:
            response = ''
            logging.debug(exc)
        else:
            if response == '':
                logging.debug("Reconnecting due to timeout")
                self.close()
                self._connect(*self.args, **self.kwargs)
                raise TimeoutError
        logging.debug("Response: %s", response.replace('\n', ''))
        return response

    def write(self, data):
        """Writes data to a driver.  It will encode to utf-8 and add a newline

        Args:
            data(str): string or list of bytes to send to the driver.
        """
        # Clear the input buffer in case it junk data go in creating an offset
        self._dev.reset_input_buffer()
        logging.debug("Sending: " + data)
        self._dev.write((data + '\n').encode('utf-8'))
