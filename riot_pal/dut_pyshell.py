#! /usr/bin/env python3
# Copyright (c) 2019 Kevin Weiss, for HAW Hamburg  <kevin.weiss@haw-hamburg.de>
#
# This file is subject to the terms and conditions of the MIT License. See the
# file LICENSE in the top level directory for more details.
# SPDX-License-Identifier:    MIT

"""
This script handles interfacing to riot DUT firmware.  It parses data and
exposes from the dut_shell class to be run in a shell.

The purpose of this script is allow easy setup and manual usage of the DUT.

Usage
-----

```
usage: dut_pyshell.py   [-h]
                        [--loglevel {debug,info,warning,error,fatal,critical}]
                        [--port PORT]
                        [--raw-data]

optional arguments:
  --help, -h
                        show this help message and exit
  --loglevel, -l
                        {debug,info,warning,error,fatal,critical}
                        Python logger log level (default: warning)
  --port, -p
                        Specify the serial port
  --rawdata, -r
                        Shows unfilted data, usually raw json
                        (default: False)
```
"""
import cmd
from json import dumps
import logging
import argparse

try:
    import readline
except ImportError:
    readline = None
import serial.tools.list_ports
try:
    from .dut_shell import DutShell, RESULT_SUCCESS
except ImportError:
    from dut_shell import DutShell, RESULT_SUCCESS


class DutPyShell(cmd.Cmd):
    """Command loop for the PHiLIP interface

    Args:
        port - Serial port for the PHiLIP, if None connection wizard tries to
               connent
        data_only - If true only data prints from command an not the whole
                    response struct
    """
    prompt = 'node: '

    def __init__(self, port=None, rawdata=False):
        if port is None:
            self.dut = self._connect_wizard()
        else:
            self.dut = DutShell(port, parser='json')
        self.cmd_list = self.dut.send_cmd('help')['data']
        self.data_only = not rawdata
        cmd.Cmd.__init__(self)

    @staticmethod
    def _connect_wizard():
        print("Starting DUT python shell")
        serial_devices = serial.tools.list_ports.comports()
        if len(serial_devices) == 0:
            raise ConnectionError("Could not find any available devices")
        elif len(serial_devices) == 1:
            print('Connected to {}'.format(serial_devices[0]))
            return DutShell(port=serial_devices[0][0], parser='json')
        else:
            print('Select a serial port:')
            for i, s_dev in enumerate(serial_devices):
                print("{}: {}".format(i, s_dev))
            s_num = int(input("Selection(number): "))
            return DutShell(port=serial_devices[int(s_num)][0], parser='json')

    def preloop(self):
        """Used to get the history of commands"""
        if readline:
            try:
                readline.read_history_file()
            except IOError:
                pass

    def do_send_cmd(self, arg):
        """Sends a command to the shell

        Usage:
            send_cmd <cmd_name> [args]

        Args:
            cmd_name: The name of the command
            args: Arguements for the command

        """
        try:
            results = self.dut.send_cmd(arg)
        except KeyError as exc:
            print('Could not parse argument {}'.format(exc))
        except (TypeError, ValueError, SyntaxError) as exc:
            print(exc)
        else:
            self._print_func_result_success(results)

    def complete_send_cmd(self, text, line, begidx, endidx):
        """Completes arg with command list"""
        begidx = begidx
        endidx = endidx
        return self._complete_cmd_list(text, line)

    def _complete_cmd_list(self, text, line):
        mline = line.partition(' ')[2]
        offs = len(mline) - len(text)
        return [s[offs:] for s in self.cmd_list if s.startswith(mline)]

    def do_rawdata(self, arg):
        """Sets raw or filtered data

        Usage:
            rawdata [val]

        Args:
            val: if 'on' then raw data, if 'off' than filtered
        """
        if arg:
            if arg.upper() == "OFF":
                self.data_only = True
                print("Filtering for data")
            elif arg.upper() == "ON":
                self.data_only = False
                print("Raw data, no filtering")
            else:
                print("Incorrect arg")
        elif self.data_only:
            self.data_only = False
            print("Raw data, no filtering")
        else:
            self.data_only = True
            print("Filtering for data")

    @staticmethod
    def complete_rawdata(text, line, begidx, endidx):
        """Completes arg filter option"""
        begidx = begidx
        endidx = endidx
        mline = line.partition(' ')[2]
        offs = len(mline) - len(text)
        filter_options = ['on', 'off']
        return [s[offs:] for s in filter_options if s.startswith(mline)]

    @staticmethod
    def do_exit(arg):
        """I mean it should be obvious

        Usage:
            exit
        """
        arg = arg
        return True

    def _print_func_result_success(self, results):
        if not isinstance(results, list):
            results = [results]
        result = RESULT_SUCCESS
        printed_something = False
        for res in results:
            if self.data_only and 'result' in res:

                if res['result'] == RESULT_SUCCESS:
                    if 'data' in res:
                        for data in res['data']:
                            print(dumps(data))
                            printed_something = True
                else:
                    result = res['result']
            else:
                print(dumps(res))
                printed_something = True
        if not printed_something:
            print(result)

    def _print_func_result(self, func, arg):
        values = (arg or '').split(' ')
        func_args = [v for v in values if v]
        try:
            results = func(*func_args)
        except KeyError as exc:
            print('Could not parse argument {}'.format(exc))
        except (TypeError, ValueError, SyntaxError) as exc:
            print(exc)
        else:
            self._print_func_result_success(results)


def _exit_cmd_loop():
    if readline:
        try:
            readline.write_history_file()
        except IOError:
            pass


def main():
    """Main program"""

    parser = argparse.ArgumentParser()

    log_levels = ('debug', 'info', 'warning', 'error', 'fatal', 'critical')
    parser.add_argument('--loglevel', '-l', choices=log_levels,
                        default='warning', help='Python logger log level')
    parser.add_argument('--port', '-p', help='Specifies the serial port',
                        default=None)
    parser.add_argument('--rawdata', '-r', default=False,
                        action='store_true',
                        help='Shows unfilted data, usually raw json')
    pargs = parser.parse_args()

    logging.basicConfig(level=getattr(logging, pargs.loglevel.upper()))
    try:
        DutPyShell(port=pargs.port, rawdata=pargs.rawdata).cmdloop()
        _exit_cmd_loop()
    except KeyboardInterrupt:
        _exit_cmd_loop()


if __name__ == '__main__':
    main()
