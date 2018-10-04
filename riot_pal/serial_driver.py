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
import serial
import serial.tools.list_ports


class SerialDriver:
    """Contains all reusable functions for connecting, sending and recieveing
    data.
    """
    DEFAULT_TIMEOUT = 1
    DEFAULT_BAUDRATE = 115200
    DEFAULT_PORT = '/dev/ttyACM0'

    used_devices = []

    def __init__(self, *args, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.DEFAULT_TIMEOUT
        if len(args) < 2:
            if 'baudrate' not in kwargs:
                kwargs['baudrate'] = self.DEFAULT_BAUDRATE
        if len(args) == 0:
            if 'port' not in kwargs:
                kwargs['port'] = self.DEFAULT_PORT
        logging.debug("Serial connection args %r -- %r", args, kwargs)

        try:
            self._dev = serial.Serial(*args, **kwargs)
        except serial.SerialException:
            self._dev = serial.serial_for_url(*args, **kwargs)

        SerialDriver.used_devices.append(self._dev.port)
        time.sleep(0.1)
        # A time delay is needed ensure everything is flushed correctly
        self._dev.reset_input_buffer()
        self._dev.reset_output_buffer()

    def close(self):
        """Close serial connection."""
        logging.debug("Closing %s", self._dev.port)
        SerialDriver.used_devices.remove(self._dev.port)
        self._dev.close()

    def read(self):
        """Read and decode data."""
        try:
            res_bytes = self._dev.readline()
            response = res_bytes.decode("utf-8", errors="replace")
        except Exception as exc:
            response = 'ERR'
            logging.debug(exc)
        logging.debug("Response: %s", response.replace('\n', ''))
        return response

    def write(self, data):
        """Tries write data."""
        logging.debug("Sending: " + data)
        self._dev.write((data + '\n').encode('utf-8'))

    @staticmethod
    def get_configs(baudrate=DEFAULT_BAUDRATE, timeout=1):
        """Gets available serial configurations."""
        portlist = serial.tools.list_ports.comports()
        available_configs = []
        for element in portlist:
            if element.device not in SerialDriver.used_devices:
                available_configs.append({'port': element.device,
                                          'baudrate': baudrate,
                                          'timeout': timeout})
        logging.debug("Ports available: %r", available_configs)
        return available_configs
