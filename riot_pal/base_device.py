# Copyright (c) 2018 Kevin Weiss, for HAW Hamburg  <kevin.weiss@haw-hamburg.de>
#
# This file is subject to the terms and conditions of the MIT License. See the
# file LICENSE in the top level directory for more details.
# SPDX-License-Identifier:    MIT
"""Abstract Base Device for RIOT PAL
This module is the abstract device that interfaces to a driver.  It handles the
selection and initialzation of the driver.

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
        driver_type(str): Selects the driver that is used on the devices.
            'serial' uses the standard serial port, all following arguments
            get passed through.
            'riot' uses the riot make term system.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
    """

    def __init__(self, driver_type='serial', *args, **kwargs):
        self._driver = self._driver_from_config(driver_type, *args, **kwargs)

    def close(self):
        """Closes the device connection."""
        self._driver.close()

    def _read(self):
        """Reads data from the driver.

        Returns:
            str: string of data if success, driver defined error if failed.
        """
        return self._driver.read()

    def _write(self, data):
        """Writes data to the driver.

        Args:
            data(str): Variable length argument list.
        """
        return self._driver.write(data)

    @staticmethod
    def _driver_from_config(driver_type='serial', *args, **kwargs):
        """Returns driver instance given configuration"""
        if driver_type == 'serial':
            return SerialDriver(*args, **kwargs)
        elif driver_type == 'riot':
            return RiotDriver(*args, **kwargs)
        elif driver_type == 'driver':
            return kwargs['driver']
        raise NotImplementedError()

    @classmethod
    def copy_driver(cls, device):
        """Copies the driver instance so many devices can use one driver."""
        # pylint: disable=W0212
        logging.debug("Cloning Driver: %r", device._driver)
        return cls(driver_type='driver', driver=device._driver)
