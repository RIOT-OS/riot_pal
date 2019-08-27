# Copyright (c) 2018 Kevin Weiss, for HAW Hamburg  <kevin.weiss@haw-hamburg.de>
#
# This file is subject to the terms and conditions of the MIT License. See the
# file LICENSE in the top level directory for more details.
# SPDX-License-Identifier:    MIT
"""Device Under Tests Shell for RIOT PAL
This module handles parsing of information from RIOT shell base tests.
"""
import logging
import json
try:
    from .base_device import BaseDevice
except ImportError:
    from base_device import BaseDevice

RESULT_SUCCESS = 'Success'
RESULT_ERROR = 'Error'
RESULT_TIMEOUT = 'Timeout'


class ShellParser:
    """Parses commands and resposes from the shell."""
    COMMAND = 'Command: '
    SUCCESS = 'Success: '
    ERROR = 'Error: '
    TIMEOUT = 'Timeout: '

    def __init__(self, dev):
        self.dev = dev

    @staticmethod
    def _try_parse_data(data):
        if ('[' in data) and (']' in data):
            parsed_data = []
            data = data[data.find("[")+1:data.find("]")]
            data_list = data.split(', ')
            for value in data_list:
                try:
                    parsed_data.append(int(value, 0))
                except ValueError:
                    parsed_data.append(value)
            logging.debug(parsed_data)
            return parsed_data
        return None

    def send_and_parse_cmd(self, send_cmd):
        """Returns a dictionary with information from the event.

        Returns:
            dict:
            The return hold dict values in the following keys::
                msg - The message from the response, only used for information.
                cmd - The command sent, used to track what has occured.
                data - Parsed information of the data requested.
                result - Either success, error or timeout.
        """
        # pylint: disable=W0212
        self.dev._write(send_cmd)
        # pylint: disable=W0212
        response = self.dev._readline()
        cmd_info = {'cmd': send_cmd, 'data': None}
        while response != '':
            if self.COMMAND in response:
                cmd_info['msg'] = response.replace(self.COMMAND, '')
                cmd_info['cmd'] = cmd_info['msg'].replace('\n', '')

            if self.SUCCESS in response:
                clean_msg = response.replace(self.SUCCESS, '')
                cmd_info['msg'] = clean_msg.replace('\n', '')
                cmd_info['result'] = RESULT_SUCCESS
                cmd_info['data'] = self._try_parse_data(cmd_info['msg'])
                break

            if self.ERROR in response:
                clean_msg = response.replace(self.ERROR, '')
                cmd_info['msg'] = clean_msg.replace('\n', '')
                cmd_info['result'] = RESULT_ERROR
                break
            # pylint: disable=W0212
            response = self.dev._readline()

        if response == '':
            cmd_info['result'] = RESULT_TIMEOUT
            logging.debug(RESULT_TIMEOUT)
        return cmd_info


class JSONParser:
    """Handles parsing of specific json data

    Args:
        dev -> device to connect send and recieve data
    """

    def __init__(self, dev):
        self.dev = dev

    def _send_cmd(self, cmd_to_send, end_key='result'):
        # pylint: disable=W0212
        self.dev._write(cmd_to_send)
        cmd_info = {}
        while end_key not in cmd_info:
            line = ""
            try:
                # pylint: disable=W0212
                line = self.dev._readline()
                cmd_info.update(json.loads(line))
            except json.decoder.JSONDecodeError:
                if 'msg' not in cmd_info:
                    cmd_info['msg'] = []
                cmd_info['msg'].append(line)
            except TimeoutError:
                cmd_info['result'] = RESULT_TIMEOUT
        return cmd_info

    def send_and_parse_cmd(self, cmd_to_send):
        """Returns a dictionary with information from the event
        Args:
            send_cmd(str): The command to write to the device
            to_byte_array: If True and data is bytes leave it as an array
            timeout: Optional timeout value for command specific timeouts
        Returns:
            dict:
            The return hold dict values in the following keys::
            msg - The message from the response, only used for information.
            cmd - The command sent, used to track what has occured.
            data - Parsed information of the data requested.
            result - Either success, error or timeout.
        """

        cmd_info = {'cmd': cmd_to_send}
        cmd_info.update(self._send_cmd(cmd_to_send))
        return cmd_info


class DutShell:
    """Device Under Test shell class
    Args:
        parser(str): Selects the parser to use {shell, json}
    """

    def __init__(self, *args, **kwargs):
        self.parser = None

        parser = kwargs.pop('parser', 'shell')

        self.dev = BaseDevice(*args, **kwargs)
        if parser == 'shell':
            self.parser = ShellParser(self.dev)
        elif parser == 'json':
            # pylint: disable=R0204
            self.parser = JSONParser(self.dev)
        else:
            raise NotImplementedError()

    def send_cmd(self, cmd_to_send, *args, **kwargs):
        return self.parser.send_and_parse_cmd(cmd_to_send, *args, **kwargs)
