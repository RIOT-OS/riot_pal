# Copyright (c) 2018 Kevin Weiss, for HAW Hamburg  <kevin.weiss@haw-hamburg.de>
#
# This file is subject to the terms and conditions of the MIT License. See the
# file LICENSE in the top level directory for more details.
# SPDX-License-Identifier:    MIT
"""RIOT Driver for RIOT PAL
This module handles generic connection and IO to the make term.
"""
import logging
import os
import pexpect


class RiotDriver:
    """Contains all reusable functions for connecting, sending and receiving
    data.
    """

    def __init__(self, timeout=5, path=None):
        if path is not None:
            os.chdir(path)
        self.child = pexpect.spawnu("make term", timeout=timeout,
                                    codec_errors='replace')

    def close(self):
        """Closes the spawned process"""
        self.child.close()

    def readline(self):
        """Reads a line from a make term process and strips away all additional
        data so only the output of the device is left."""
        try:
            response = self.child.readline()
            response = response.split('# ', 1)[-1]
            response = response.replace('\n', '')
            response = response.replace('\r', '')
        except (ValueError, TypeError, pexpect.TIMEOUT) as exc:
            logging.debug(exc)
            response = "ERR"
        logging.debug("Response: %s", response)
        return response

    def write(self, data):
        """Tries write data and adds a newline."""
        logging.debug("Writing: %s", data)
        self.child.write(data + '\n')
