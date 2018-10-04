# Copyright (c) 2018 Kevin Weiss, for HAW Hamburg  <kevin.weiss@haw-hamburg.de>
#
# This file is subject to the terms and conditions of the MIT License. See the
# file LICENSE in the top level directory for more details.
# SPDX-License-Identifier:    MIT
"""Abstract Base Device for RIOT PAL
This module is the abstract device that interfaces to a driver.  It handles
the selection and initialzation of the driver.

Example:
    class ApplicationDevice(BaseDevice):
        def show_example(self):
            self._write('Send Example')
            print(self._read())

    example_use_case = ApplicationDevice('serial', port='my/port/name')
    example_use_case.show_example()
"""
import logging
from .serial_driver import SerialDriver
from .riot_driver import RiotDriver


class BaseDevice:
    """Instance for devices to connect and utilize drivers.

    Args:
        dev_type(str): Specify the type of driver to use.
            serial, riot, driver are valid inputs
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
    """

    def __init__(self, driver_type='serial', *args, **kwargs):
        if driver_type == 'serial':
            self._driver = SerialDriver(*args, **kwargs)
        elif driver_type == 'riot':
            self._driver = RiotDriver(*args, **kwargs)
        elif driver_type == 'driver':
            self._driver = kwargs['driver']
        else:
            raise NotImplementedError()

    def close(self):
        """Closes the device connection."""
        self._driver.close()

        #
    def _driver_from_config(self, dev_type='serial', *args, **kwargs):
        """Returns driver instance given configuration"""
        if dev_type == 'serial':
            return SerialDriver(*args, **kwargs)
        elif dev_type == 'riot':
            return RiotDriver(*args, **kwargs)
        elif dev_type == 'driver':
            return kwargs['driver']
        raise NotImplementedError()

    def _read(self):
        """Reads data from the driver.

        Returns:
            str: string of data if success, ERR string if failed
        """
        return self._driver.read()

    def _write(self, data):
        """Writes data to the driver.

        Args:
            data(str): Variable length argument list.
        """
        return self._driver.write(data)

    @classmethod
    def copy_driver(cls, device):
        """Copies the driver instance so many devices can use one driver."""
        logging.debug("Cloning Driver: %r", device._driver)
        return cls(driver_type='driver', driver=device._driver)
