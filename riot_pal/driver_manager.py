# Copyright (c) 2018 Kevin Weiss, for HAW Hamburg  <kevin.weiss@haw-hamburg.de>
#
# This file is subject to the terms and conditions of the MIT License. See the
# file LICENSE in the top level directory for more details.
# SPDX-License-Identifier:    MIT
"""Driver Manager for RIOT PAL
This module assigns drivers to devices.
"""
import logging
try:
    from .serial_driver import SerialDriver
    from .riot_driver import RiotDriver
except SystemError:
    from serial_driver import SerialDriver
    from riot_driver import RiotDriver


def driver_from_config(dev_type='serial', *args, **kwargs):
    """Returns driver instance given configuration"""
    if dev_type == 'serial':
        return SerialDriver(*args, **kwargs)
    elif dev_type == 'riot':
        return RiotDriver(*args, **kwargs)
    elif dev_type == 'driver':
        return kwargs['driver']
    raise NotImplementedError()


def available_configs(dev_type='serial', *args, **kwargs):
    """Returns possible configurations to attempt to connect to."""
    if dev_type == 'serial':
        return SerialDriver.get_configs(*args, **kwargs)
    elif dev_type == 'riot':
        return RiotDriver.get_configs(*args, **kwargs)
    raise NotImplementedError()


def main():
    """Tests basic usage of the class"""
    logging.getLogger().setLevel(logging.DEBUG)
    logging.debug(available_configs())
    logging.debug(driver_from_config())


if __name__ == "__main__":
    main()
