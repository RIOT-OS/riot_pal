RIOT PAL (RIOT Protocol Abstraction Layer)
================================

Introduction
------------

A set of python modules that abstract away and standardize shell based commands in RIOT and for bare metal memory map access.


### Usage of LLMemMapIf
The LLMemMapIf (Low Level Memory Map Interface) is used to interface to a memory map specified from a csv or other format file.  It handles the parsing of offsets, sizes, etc. of the device.

To use this interface a memory must be provided, by default the package contains the PHiLIP memory map.  More information about PHiLIP can be found at the [PHiLIP repo](https://github.com/riot-appstore/PHiLIP).

PHILIP_MEM_MAP_PATH - Provides a path to the csv used for updating the list of commands for the LLMemMapIf</br></br>
read_struct - Reads a set of registers defined by the memory map.</br></br>
read_reg - Read a register defined by the memory map.
* cmd_name(str): The name of the register to read.
* offset(int): The number of elements to offset in an array.
* size(int): The number of elements to read in an array.

write_reg - Writes a register defined by the memory map.
* cmd_name(str): The name of the register to read
* data: The data to write to the register
* offset(int): The number of elements to offset in an array.

### Example with PHiLIP
1. Install riot_pal from pip</br>`pip install riot_pal`
2. Start python 3</br>`python3`
3. Create a import modules from riot pal</br>`>>> from riot_pal import LLMemMapIf, PHILIP_MEM_MAP_PATH`
4. Create a connection</br>`>>> phil = LLMemMapIf(PHILIP_MEM_MAP_PATH, 'serial', '/dev/ttyACM0')`
5. View available commands</br>`>>> phil.cmd_list.keys()`
6. View descriptions of commands</br>`>>> phil.cmd_list['sys.sn.12']['description']`
7. Read a register</br>`>>> phil.read_reg('sys.sn.12')`
8. Only view data</br>`>>> phil.read_reg('sys.sn.12')['data']`
9. Write bytes to a register</br>`>>> phil.write_reg('user_reg.64', [4, 2])`
10. Read new data</br>`>>> phil.read_reg('user_reg.64', size=10)['data']`
11. Write a number to a register</br>`>>> phil.write_reg('user_reg.64', 42)`
12. Read new data</br>`>>> phil.read_reg('user_reg.64', size=4)['data']`
13. Read a structure</br>`>>> phil.read_struct('sys')`
