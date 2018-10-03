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
try:
    from . import driver_manager
except SystemError:
    import driver_manager


class BaseDevice:
    """Instance for devices to connect and utilize drivers.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
    """

    def __init__(self, *args, **kwargs):
        self._driver = driver_manager.driver_from_config(*args, **kwargs)

    def close(self):
        """Closes the device connection."""
        self._driver.close()

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

    def is_connected_to_board(self):
        """Dummy - confirm if a connection is for target board."""
        logging.warning("Check if board is connected: dummy should be"
                        " implmeneted in subclasses")
        raise NotImplementedError()

    @classmethod
    def from_autodetect(cls, *args, **dev_config):
        """Connects to a range of possible configurations."""
        configs = driver_manager.available_configs(*args, **dev_config)
        logging.debug("Configs: %r", configs)
        for config in configs:
            for retry in range(0, 2):
                logging.debug("Autodetect attempt: %d", retry)
                conn = cls(**config)
                try:
                    if conn.is_connected_to_board():
                        return conn
                except Exception as err:
                    logging.debug("Cannot connect: %r", err)
                conn.close()

        raise ValueError("Could not locate board, check if board is"
                         "connected or is_connected_to_board is correct")

    @classmethod
    def copy_driver(cls, device):
        """Copies the driver instance so many devices can use one driver."""
        logging.debug("Cloning Driver: %r", device._driver)
        return cls(dev_type='driver', driver=device._driver)


def main():
    """Tests basic usage of the class

    Used for unit testing, information should be confirm with DEBUG info.
    """
    logging.getLogger().setLevel(logging.DEBUG)
    BaseDevice()


if __name__ == "__main__":
    main()
