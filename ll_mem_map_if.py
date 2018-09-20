# Copyright (C) 2018 Kevin Weiss <kevin.weiss@haw-hamburg.de>
#
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more details.
"""@package PyToAPI
This module handles offset and sizes dictated by the memory map for PHiLIP.
"""
import logging
import csv
try:
    from .ll_shell import LLShell
except SystemError:
    from ll_shell import LLShell


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
            if cmd.startswith(cmd_name):
                response.append(self.read_reg(cmd))
        return response

    def read_reg(self, cmd_name, offset=0, size=None):
        """Read a register defined by the memory map."""
        cmd = self.cmd_list[cmd_name]
        response = None
        if size is None:
            size = cmd['total_size']
        if cmd['is_bitfield'] is 'True':
            response = self.read_bits(cmd['offset'], cmd['bit_offset'], cmd['bits'])
        elif cmd['size'] != cmd['total_size']:
            offset += int(cmd['offset'])
            if size is None:
                size = cmd['total_size']
            response = self.read_bytes(offset, size)
        else:
            response = self.read_bytes(cmd['offset'], cmd['total_size'])
        response['msg'] = 'cmd={} response={}'.format(cmd_name, response['msg'])
        return response

    def write_reg(self, cmd_name, data, offset=0):
        """Writes a register defined by the memory map."""
        cmd = self.cmd_list[cmd_name]
        response = None
        if cmd['is_bitfield'] is 'True':
            response = self.write_bits(cmd['offset'], cmd['bit_offset'], cmd['bits'], data)
        elif cmd['size'] != cmd['total_size']:
            offset += int(cmd['offset'])
            response = self.write_bytes(offset, data)
        else:
            response = self.write_bytes(cmd['offset'], data)
        response['msg'] = 'cmd={} response={}'.format(cmd_name, response['msg'])
        return response

def main():
    from pprint import pprint
    """Tests all functions supported functions."""
    logging.getLogger().setLevel(logging.DEBUG)

    mmif = LLMemMapIf("mem_map.csv", 'serial', '/dev/ttyUSB0')
    print('==================================================================')
    pprint(mmif.read_struct('sys'))
    pprint(mmif.read_reg('user_reg.64', 0, 10))
    pprint(mmif.write_reg('user_reg.64', [6, 6, 6], 2))
    pprint(mmif.read_reg('user_reg.64'))
    pprint(mmif.cmd_list)

if __name__ == "__main__":
    main()
