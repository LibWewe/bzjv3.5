#!usr/bin/env python  
# -*- coding:utf-8 -*-  
""" 
@file: bzjModbusSlave.py
@version: v1.0 
@author: WeWe 
@time: 2018/07/23 11:16
@lib v: Python 3.6.4 /2.7.14
@description:This file is fro ...  
"""
from modbus_tk import defines, modbus_tcp, utils
import time


def func():
    pass


class bzjModbusSlave():
    def __init__(self):
        self.Logger = utils.create_logger(name="console")  # record_format="%(message)s"
        self.server = modbus_tcp.TcpServer()  # address="192.168.8.25"

    def start(self):
        self.server.start()

    def stop(self):
        self.server.stop()


def main():
    bzjModbus = bzjModbusSlave()
    bzjModbus.start()
    connection = len(bzjModbus.server._sockets)
    print(connection)
    slave = bzjModbus.server.add_slave(slave_id=1)
    slave.add_block(block_name="1", block_type=defines.HOLDING_REGISTERS, starting_address=0, size=10)
    slave.add_block(block_name="2", block_type=defines.COILS, starting_address=0, size=10)
    slave.add_block(block_name="3", block_type=defines.HOLDING_REGISTERS, starting_address=10, size=10)
    slave.set_values(block_name="1", address=0,
                     values=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    slave.set_values(block_name="2", address=0, values=[0, 1, 1, 0, 0, 1, 1, 1, 0, 0])
    slave.set_values(block_name="3", address=10, values=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    while True:
        block2_1 = slave.get_values(block_name="2", address=0, size=10)
        print("block2_1:", block2_1)
        if block2_1[0] == 1:
            block1 = list(slave.get_values(block_name="1", address=0, size=10))
            print("block1:", block1, type(block1), type(block1[0]))
            block1[0] = 100
            slave.set_values(block_name="1", address=0, values=[block1[0], 65535])
        time.sleep(2)
        count = len(bzjModbus.server._sockets)
        print("count:", count)
        block3 = slave.get_values(block_name="3", address=10, size=10)
        print("block3:", block3, type(block3[0]))


if __name__ == "__main__":
    main()
    pass
