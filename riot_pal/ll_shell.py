# Copyright (c) 2018 Kevin Weiss, for HAW Hamburg  <kevin.weiss@haw-hamburg.de>
#
# This file is subject to the terms and conditions of the MIT License. See the
# file LICENSE in the top level directory for more details.
# SPDX-License-Identifier:    MIT
"""Low Level Shell for RIOT PAL
This module handles functions for a low level shell interface.
"""
import logging
import errno
import os
from .base_device import BaseDevice


class LLShell(BaseDevice):
    """Handles basic functions and commands for memory map interface."""
    READ_REG_CMD = "rr"
    WRITE_REG_CMD = "wr"
    EXECUTE_CMD = "ex"
    RESET_CMD = "mcu_rst"
    SUCCESS = '0'
    RESET_SUCCESS = '\x000'
    RESULT_SUCCESS = 'Success'
    RESULT_ERROR = 'Error'
    RESULT_TIMEOUT = 'Timeout'

    @staticmethod
    def _try_parse_data(data):
        if len(data) > 1:
            # response contains data
            try:
                if len(data[1]) - 2 <= 8:
                    return int(data[1], 0)
                elif data[1].startswith('0x'):
                    data = bytearray.fromhex(data[1][2:])
                    return list(data[::-1])
                else:
                    return data[1:]
            except ValueError:
                return data[1:]

        return None

    @staticmethod
    def _error_msg(data):
        s_errcode = errno.errorcode[data]
        s_errmsg = os.strerror(data)
        return "{}-{} [{}]".format(s_errcode, s_errmsg, data)

    def _populate_cmd_info(self, data):
        cmd_info = {}
        try:
            # handle case if reset occurs and there is a 0 in the buffer
            if data[0] == self.RESET_SUCCESS:
                data[0] = self.SUCCESS
            if data[0] == self.SUCCESS:
                cmd_info['data'] = self._try_parse_data(data)
                cmd_info['msg'] = "EOK-command success [0]"
                cmd_info['result'] = self.RESULT_SUCCESS
                logging.debug(self.RESULT_SUCCESS)
            else:
                # put error code in data
                cmd_info['data'] = int(data[0], 0)
                cmd_info['msg'] = self._error_msg(cmd_info['data'])
                cmd_info['result'] = self.RESULT_ERROR
                logging.debug(self.RESULT_ERROR)
                logging.debug(cmd_info['msg'])
        except (ValueError, TypeError, AttributeError) as exc:
            cmd_info['msg'] = "Unknown Error {}".format(exc)
            cmd_info['data'] = data[0]
            cmd_info['result'] = self.RESULT_ERROR
            logging.debug(self.RESULT_ERROR)
            logging.debug(exc)
        return cmd_info

    def send_cmd(self, send_cmd):
        """Returns a dictionary with information from the event.
        Returns:
            dict:
            The return hold dict values in the following keys::
            msg - The message from the response, only used for information.
            cmd - The command sent, used to track what has occured.
            data - Parsed information of the data requested.
            result - Either success, error or timeout.
        """
        self._write(send_cmd)
        data = self._read()
        cmd_info = {'cmd': send_cmd}
        if data == "":
            cmd_info['msg'] = "Timeout occured"
            cmd_info['data'] = None
            cmd_info['result'] = self.RESULT_TIMEOUT
            logging.debug(self.RESULT_TIMEOUT)
        else:
            data = data.replace('\n', '')
            data = data.split(',')
            cmd_info.update(self._populate_cmd_info(data))
        return cmd_info

    def read_bytes(self, index, size=1):
        """Reads bytes in the register map."""
        logging.debug("FXN: read_bytes(%r,%r)", index, size)
        cmd = '{} {} {}'.format(self.READ_REG_CMD, index, size)
        return self.send_cmd(cmd)

    def write_bytes(self, index, data, size=4):
        """Writes bytes in the register map."""
        logging.debug("FXN: write_bytes(%r,%r)", index, data)
        cmd = "{} {}".format(self.WRITE_REG_CMD, index)
        if isinstance(data, list):
            if isinstance(data[0], str):
                if data[0].startswith('0x'):
                    data = data[0].replace('0x', '')
                    data = bytes.fromhex(data)
            for i in range(0, len(data)):
                if len(data) - i - 1 < len(data):
                    cmd += ' {}'.format(data[len(data) - i - 1])
                else:
                    cmd += ' 0'
        else:
            for i in range(0, size):
                cmd += ' {}'.format((data >> ((i) * 8)) & 0xFF)
        return self.send_cmd(cmd)

    def read_bits(self, index, offset, bit_amount):
        """Read specific bits in the register map."""
        bit_amount = int(bit_amount)
        offset = int(offset)
        index = int(index)
        logging.debug("FXN: read_bits(%r, %r, %r)", index, offset, bit_amount)
        bytes_to_read = int((bit_amount - 1 + offset)/8 + 1)
        bit_mask = (2 ** bit_amount) - 1
        cmd_info = self.read_bytes(index, bytes_to_read)
        if cmd_info['result'] == self.RESULT_SUCCESS:
            cmd_info['cmd'] += ', read_bits {} {} {}'.format(index, offset,
                                                             bit_amount)
            cmd_info['data'] = cmd_info['data'] >> offset
            cmd_info['data'] = cmd_info['data'] & bit_mask

        logging.debug("Bits: %r", cmd_info['data'])
        return cmd_info

    def write_bits(self, index, offset, bit_amount, data):
        """Modifies specific bits in the register map."""
        bit_amount = int(bit_amount)
        offset = int(offset)
        index = int(index)
        cmd_sent = ""
        logging.debug("FXN: write_bits"
                      "(%r, %r, %r, %r)", index, offset, bit_amount, data)
        bytes_to_read = int((bit_amount - 1 + offset)/8 + 1)
        cmd_info = self.read_bytes(index, bytes_to_read)
        if cmd_info['result'] != self.RESULT_SUCCESS:
            return cmd_info
        cmd_sent += cmd_info['cmd']
        bit_mask = int((2 ** bit_amount) - 1)
        bit_mask = bit_mask << offset
        cmd_info['data'] = cmd_info['data'] & (~bit_mask)
        shifted_data = cmd_info['data'] | ((data << offset) & bit_mask)
        cmd_info = self.write_bytes(index, shifted_data, bytes_to_read)
        cmd_sent += cmd_info['cmd']
        if cmd_info['result'] == self.RESULT_SUCCESS:
            cmd_sent += ',write_bits {} {} {} {}'.format(index, offset,
                                                         bit_amount, data)
        cmd_info['cmd'] = cmd_sent
        return cmd_info

    def execute_changes(self):
        """Executes device configuration changes."""
        logging.debug("FXN: execute_changes")
        return self.send_cmd(self.EXECUTE_CMD)

    def reset_mcu(self):
        """Resets the device."""
        logging.debug("FXN: reset_mcu")
        return self.send_cmd(self.RESET_CMD)
