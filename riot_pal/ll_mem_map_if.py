# Copyright (c) 2018 Kevin Weiss, for HAW Hamburg  <kevin.weiss@haw-hamburg.de>
#
# This file is subject to the terms and conditions of the MIT License. See the
# file LICENSE in the top level directory for more details.
# SPDX-License-Identifier:    MIT
"""Low Level Memory Map Interface for RIOT PAL
This module handles offset and sizes dictated a memory map.
"""
import logging
import csv
from .ll_shell import LLShell


class LLMemMapIf(LLShell):
    """Interface between ll_shell and mem_map."""

    def __init__(self, path, *args, **kwargs):
        self.cmd_list = LLMemMapIf.import_mm_from_csv(path)
        super().__init__(*args, **kwargs)

    @staticmethod
    def import_mm_from_csv(path):
        """Imports a memory map csv file."""
        cmd_list = {}
        with open(path) as csvfile:
            rows = list(csv.reader(csvfile, quotechar="'"))
            for row in range(1, len(rows)):
                cmd = dict(zip(rows[0], rows[row]))
                cmd_list[rows[row][rows[0].index('name')]] = cmd
                logging.debug("Imported command: %r", cmd)
        return cmd_list

    def read_struct(self, cmd_name):
        """Reads a set of registers defined by the memory map."""
        response = []
        for cmd, val in self.cmd_list.items():
            # Supress unused variable warning
            val = val
            if cmd.startswith(cmd_name):
                response.append(self.read_reg(cmd))
        return response

    def read_reg(self, cmd_name, offset=0, size=None):
        """Read a register defined by the memory map.

        Args:
            cmd_name(str): The name of the register to read.
            offset(int): The number of elements to offset in an array.
            size(int): The number of elements to read in an array.
        """
        cmd = self.cmd_list[cmd_name]
        response = None
        if size is None:
            size = cmd['total_size']
        if 'True' in cmd['is_bitfield']:
            response = self.read_bits(cmd['offset'],
                                      cmd['bit_offset'],
                                      cmd['bits'])
        elif cmd['size'] != cmd['total_size']:
            offset = int(cmd['offset']) + (offset * int(cmd['size']))
            if size is None:
                size = cmd['total_size']
            else:
                size = size * int(cmd['size'])
            response = self.read_bytes(offset, size)
        else:
            response = self.read_bytes(cmd['offset'], cmd['total_size'])
        response['msg'] = 'cmd={} response={}'.format(cmd_name,
                                                      response['msg'])
        return response

    def write_reg(self, cmd_name, data, offset=0):
        """Writes a register defined by the memory map.

        Args:
            cmd_name(str): The name of the register to read.
            data: The data to write to the register.
            offset(int): The number of elements to offset in an array.
        """
        cmd = self.cmd_list[cmd_name]
        response = None
        if 'True' in cmd['is_bitfield']:
            response = self.write_bits(cmd['offset'],
                                       cmd['bit_offset'],
                                       cmd['bits'], data)
        elif cmd['size'] != cmd['total_size']:
            offset = int(cmd['offset']) + (offset * int(cmd['size']))
            response = self.write_bytes(offset, data)
        else:
            response = self.write_bytes(cmd['offset'], data, int(cmd['size']))
        response['msg'] = 'cmd={} response={}'.format(cmd_name,
                                                      response['msg'])
        return response
