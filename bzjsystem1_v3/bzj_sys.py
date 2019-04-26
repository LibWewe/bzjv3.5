#!usr/bin/env python  
# -*- coding:utf-8 -*-  
""" 
@file: bzj.py
@version: v1.0 
@author: WeWe 
@time: 2018/07/23 11:06
@lib v: Python 3.6.4
@description:This file is fro ...  
"""

from multiprocessing import Process, freeze_support
import threading
import socket
import pymysql
import time
import re
import random
import serial
import logging
from modbus_tk import defines
from bzjsystem1_v3 import logout
from bzjsystem1_v3 import bzjModbusSlave
from config import config


class PcRRegsBlock(object):
    """
    pc端读PLC数据寄存器类，包括不同情况下的工字轮编号和工字轮重量
    """
    name_list = ["spool1_id_h", "spool1_id_l",
                 "spool1_weight_h", "spool1_weight_l",
                 "spool2_id_h", "spool12_id_l",
                 "spool2_weight_h", "spool2_weight_l",
                 "spool_exit1_id_h", "spool_exit1_id_l",
                 "spool_exit2_id_h", "spool_exit2_id_l",
                 "spool_finished_id_h", "spool_finished_id_l",
                 "", "",
                 "", "",
                 "", "",
                 "", "",
                 "", "", ]

    class RegsName(object):
        """
        内部类，用于定义PC读数据数据块内各个寄存器名称
        """

        def __init__(self):
            self.spool1_id_h = "spool1_id_h"
            self.spool1_id_l = "spool1_id_l"
            self.spool1_weight_h = "spool1_weight_h"
            self.spool1_weight_l = "spool1_weight_l"
            self.spool2_id_h = "spool2_id_h"
            self.spool2_id_l = "spool12_id_l"
            self.spool2_weight_h = "spool2_weight_h"
            self.spool2_weight_l = "spool2_weight_l"
            self.spool_exit1_id_h = "spool_exit1_id_h"
            self.spool_exit1_id_l = "spool_exit1_id_l"
            self.spool_exit2_id_h = "spool_exit2_id_h"
            self.spool_exit2_id_l = "spool_exit2_id_l"
            self.spool_finished_id_h = "spool_finished_id_h"
            self.spool_finished_id_l = "spool_finished_id_l"

    regs_name = RegsName()

    def __init__(self):
        self.block_name = "pc_r_regs"
        self.block_value = []
        self.start_address = 0
        self.size = 20

    def get_reg_value(self, reg_name):
        """
        通过寄存器名称，从寄存器缓存区获取该寄存器的值
        :param reg_name: 寄存器名称
        :return:返回该寄存器的值
        """
        return self.block_value[self.name_list.index(reg_name)]

    def get_reg_address(self, reg_name):
        """
        通过寄存器名称获取寄存器的地址
        :param reg_name:寄存器的名称
        :return:返回该寄存器的address
        """
        return self.name_list.index(reg_name)


class PcWRegsBlock(object):
    """
    PC端向PLC写数据的数据寄存器，包括，扫码获取的工字轮编号的高位、低位
    """
    name_list = ["spool1_id_to_plc_h", "spool1_id_to_plc_l",
                 "", "",
                 "", "",
                 "", "",
                 "", "",
                 "", "",
                 "", "",
                 "", "",
                 "", "",
                 "", "",
                 "", "",
                 "", "", ]

    class RegsName(object):
        """
        内部类，定义了PC写数据数据块的各个寄存器的名称
        """

        def __init__(self):
            self.spool1_id_to_plc_h = "spool1_id_to_plc_h"
            self.spool1_id_to_plc_l = "spool1_id_to_plc_l"

    regs_name = RegsName()

    def __init__(self):
        self.block_name = "pc_w_regs"
        self.block_value = []
        self.start_address = 20
        self.size = 20

    def set_reg(self, reg_name, value):
        """
        通过寄存器名称，向寄存器缓存区写入数据
        :param reg_name:寄存器名称
        :param value:将要写入寄存器的值
        :return:无
        """
        self.block_value[self.name_list.index(reg_name)] = value

    def get_reg_address(self, reg_name):
        """
        通过寄存器名称获取寄存器的地址
        :param reg_name:器存取名称
        :return:寄存器地址
        """
        return self.name_list.index(reg_name) + 20


class PcRCoilsBlock(object):
    """
    PC端读取PLC信号数据块类，包括是否需要读取工字轮重量，是否有工字轮要退出，是否有工字轮已包好
    """
    name_list = ["is_scan_first", "is_get_weight_first",
                 "is_scan_second", "is_get_weight_second",
                 "is_has_exit_first", "is_has_exit_second",
                 "is_has_spool_finished", "",
                 "", "",
                 "", "",
                 "", "",
                 "", "",
                 "", "",
                 "", "",
                 "", "",
                 "", "", ]

    class RegsName(object):
        """
        内部类，用于定义PC读信号数据块内各个寄存器名称
        """

        def __init__(self):
            self.is_scan_first = "is_scan_first"
            self.is_get_weight_first = "is_get_weight_first"
            self.is_scan_second = "is_scan_second"
            self.is_get_weight_second = "is_get_weight_second"
            self.is_has_exit_first = "is_has_exit_first"
            self.is_has_exit_second = "is_has_exit_second"
            self.is_has_spool_finished = "is_has_spool_finished"

    regs_name = RegsName()

    def __init__(self):
        self.block_name = "pc_r_coils"
        self.block_value = []
        self.start_address = 0
        self.size = 20

    def get_reg_value(self, reg_name):
        """
        通过寄存器名称，从寄存器值缓存区获取该寄存器的值
        :param reg_name: 寄存器名称
        :return:返回寄存器的值
        """
        return self.block_value[self.name_list.index(reg_name)]

    def get_reg_address(self, reg_name):
        """
        通过寄存器名称获取寄存器的地址
        :param reg_name:寄存器名称
        :return:寄存器address
        """
        return self.name_list.index(reg_name)


class PcWCoilsBlock(object):
    """
    PC端向PLC发送信号的寄存器数据块，包括工字轮状况，工字轮二维码异常，miss系统异常
    """
    name_list = ["spool_next", "spool_exit",
                 "scan_failed", "miss_fault",
                 "", "",
                 "", "",
                 "", "",
                 "", "",
                 "", "",
                 "", "",
                 "", "",
                 "", "",
                 "", "",
                 "", "", ]

    class RegsName(object):
        """
        内部类，用于定义PC向PLC写信号数据块内各个寄存器名称
        """

        def __init__(self):
            self.spool_next = "spool_next"  # 工字轮号获取后，经miss系统验证通过，告诉PLC其可以进入称重阶段
            self.spool_exit = "spool_exit"  # 工字轮号获取后，经miss系统验证未通过，告诉PLC其该工字轮需要退出
            self.scan_failed = "scan_failed"  # 告诉PLC扫码枪扫描二维码失败
            self.miss_fault = "miss_fault"

    regs_name = RegsName()

    def __init__(self):
        self.block_name = "pc_w_coils"
        self.block_value = []
        self.start_address = 20
        self.size = 20

    def set_reg(self, reg_name, value):
        """
        通过寄存器名称，想寄存器数据缓存区写入数据
        :param reg_name: 寄存器名称
        :param value: 写入寄存器的值
        :return: 无
        """
        self.block_value[self.name_list.index(reg_name)] = value

    def get_reg_address(self, reg_name):
        """
        通过寄存器名称获取寄存器的地址
        :param reg_name:寄存器名称
        :return:寄存器的address
        """
        return self.name_list.index(reg_name) + 20


class BzjSystem(object):
    """
    后台逻辑处理程序类
    """

    def __init__(self):
        """
        block1  pc读数据{b0：第1称重时工字轮编号high位；b1：第1次称重时工字轮编号low位；
                         b2：工字轮第1次称重重量high位；b3：工字轮第1次称重重量low位；
                         b4：第2称重时工字轮编号high位；b5：第2次称重时工字轮编号low位；
                         b6：工字轮第2次称重重量high位；b7：工字轮第2次称重重量low位；
                         b8：通孔退出工字轮编号high位；b9：通孔退出工字轮编号low位；
                         b10：二次称重后退出工字轮编号high位；b11：二次称重后退出工字轮编号low位；
                         b12：包装完成工字轮编号high位；b13：包装完成工字轮编号low位}
        block2  pc写数据{b0：扫码工字轮编号high位(addr=20)；b2：扫码工字轮编号low位(spool_next=21)
                        }
        block3  pc读信号{b0：扫描枪是否进行第一次扫描；b1：是否读取第一次称重数据
                         b2：扫描枪是否进行第二次扫描；b3：是否读取第二次称重数据；
                         b4：通孔是否有工字轮退出；b5：二次称重后是否有工字轮退出；
                         b6：有工字轮包装完成}
        block4  pc写信号{b0：告诉plc将工字轮送入下一工序(addr=20)；b1：告诉plc将工字轮退出(addr=21)；
                         b3：告诉PLC扫码枪扫描二维码失败(addr=22)；b4：告诉PLC mess系统异常(addr=23)}

        """

        self.pc_r_regs_block = PcRRegsBlock()
        self.pc_w_regs_block = PcWRegsBlock()
        self.pc_r_coils_block = PcRCoilsBlock()
        self.pc_w_coils_block = PcWCoilsBlock()
        self.mutex = threading.Lock()  # 读取工字轮重量互斥锁
        self.mutex2 = threading.Lock()  # 程序运行信息操作消息队列互斥锁
        self.mutex3 = threading.Lock()  #
        self.signal = threading.Event()
        # self.log = logout.TimedRotatingFileLog("sys_log", ".\\log\\", "sys.log",logging.DEBUG)
        self.log = logout.RotatingFileLog("sys_log", ".\\log\\", "sys.log", logging.DEBUG)
        self.scanner_date1 = ""
        self.scanner_date2 = ""
        self.weight_date1 = 0
        self.weight_time1 = ""
        self.weight_date2 = 0
        self.weight_time2 = ""
        self.GZL_id = ""
        self.msg_list = []
        self.DEBUG = 1
        self.INFO = 2
        self.WARNING = 3
        self.ERROR = 4
        self.CRITICAL = 5
        self.q = None
        self.q_err = None
        self.q_err_msg = {
            "code": 0,
            "msgstr": "",
        }

        my_cof = config.config()
        # my_cof.cofig_update()
        my_cof.get_config()
        self.msg_level = my_cof.level["msg_level"]

        self.ip1 = my_cof.scanner["s1_ip"]  # "172.24.24.222"
        self.port1 = my_cof.scanner["s1_port"]  # 51236
        self.ip2 = my_cof.scanner["s2_ip"]  # "172.24.24.222"
        self.port2 = my_cof.scanner["s2_port"]  # 51236
        self.db = pymysql.Connect(my_cof.mysql["host"], my_cof.mysql["user"], my_cof.mysql["passwd"],
                                  my_cof.mysql["dbName"])
        self.cursor = self.db.cursor()

        self.selComPort = my_cof.sel["selComPort"]  # 获取串口的端口
        self.selBaudRate = my_cof.sel["selBaudRate"]  # 获取串口通讯的波特率

    def create_thread(self):
        """
        T1:线程1，1号扫描枪处理线程
        T2:线程2，2号扫描枪处理线程
        T3:线程3，给mess系统发送完整的工字轮信息
        T4:线程4，将逻辑处理程序运行信息传输到界面显示程序中
        T5:线程5，串口扫码枪处理线程
        T6:线程6，与PLC进行modbus通信的线程
        :return:无
        """
        self.T3 = threading.Thread(target=self.mess_date_thread, args=("T3",), kwargs={}, name="T3")
        self.T4 = threading.Thread(target=self.msg_to_win_thread, args=("T4", self.q,), kwargs={}, name="T4")
        self.T5 = threading.Thread(target=self.scanner_thread, args=("T5",), kwargs={}, name="T5")
        self.T6 = threading.Thread(target=self.modbus_thread, args=("T6",), kwargs={}, name="T6")

    def scanner_thread(self, *args, **kwargs):
        """
        串口型二维码扫码枪获取二维码数据
        :param args:args[0]线程名称
        :param kwargs:
        :return:无
        """
        self.scanner_flag = False
        while True:
            count = 0
            wait_count = 0
            while not self.scanner_flag:
                # 连接扫码枪测试
                try:
                    self.ser = serial.Serial(self.selComPort, self.selBaudRate, timeout=2)
                except Exception as e:
                    if count % 10 == 0 and count > 0:
                        self.log_msg(flag=self.ERROR, msg_str="连接扫码枪异常")
                        self.q_err_msg["code"] = 11
                        self.q_err_msg["msgstr"] = "连接扫码枪异常"
                        self.q_err.put(self.q_err_msg)
                    time.sleep(3)
                    count += 1
                else:
                    self.scanner_flag = True
                    self.log_msg(flag=self.INFO, msg_str="连接扫码枪成功")
                    self.q_err_msg["code"] = 10
                    self.q_err_msg["msgstr"] = "连接扫码枪成功"
                    self.q_err.put(self.q_err_msg)
                    count = 0
                    break
                if count > 100:
                    self.log_msg(flag=self.WARNING, msg_str="由于长时间无法成功连接扫码枪，程序无法正常运行，程序进入间歇等待状态")
                    time.sleep(30)
                    if count > 9000:
                        count = 0

            self.wait_to_connect_plc()  # 等待PLC连接，内部轮询与plc的连接状态，直到成功连接

            while self.scanner_flag:
                try:
                    # rcv = self.ser.read_all().decode("utf-8")
                    rcv = self.ser.readline().decode("utf-8")
                except Exception as e:
                    self.log_msg(flag=self.ERROR, msg_str="读取扫码枪数据出现异常")
                    self.ser.close()
                    self.scanner_flag = False
                    break
                else:
                    if rcv is not "":
                        # print(rcv)
                        if len(rcv) < 22:
                            self.log_msg(flag=self.WARNING, msg_str="扫码枪数据异常")
                        else:
                            rcv1 = rcv[:-2]
                            if self.is_number(rcv1):
                                print(rcv1)
                                self.scanner_date1 = rcv1
                                self.log_msg(flag=self.INFO, msg_str="成功读取二维码数据")

                                if not self.is_connect_to_plc():  # 判断是否与PLC通信连接是否成功
                                    break

                                id_high = 200
                                id_low = 3000
                                self.set_block_values(self.pc_w_regs_block.block_name,
                                                      self.pc_w_regs_block.get_reg_address(
                                                          self.pc_w_regs_block.regs_name.spool1_id_to_plc_h),
                                                      values=[id_high, ])
                                self.set_block_values(self.pc_w_regs_block.block_name,
                                                      self.pc_w_regs_block.get_reg_address(
                                                          self.pc_w_regs_block.regs_name.spool1_id_to_plc_l),
                                                      values=[id_low, ])
                                self.set_block_values(self.pc_w_coils_block.block_name,
                                                      self.pc_w_coils_block.get_reg_address(
                                                          self.pc_w_coils_block.regs_name.spool_next), values=[1, ])
                time.sleep(0.2)

    def mess_date_thread(self, *args, **kwargs):
        """
        与mess系统通信程序
        :param args:args[0]线程名称
        :param kwargs:
        :return:无
        """
        while True:
            self.signal.wait()
            self.signal.clear()
            # 获取工字轮信息
            sqlstr = "SELECT * FROM gongzilun WHERE gongzilunid='%s'" % self.GZL_id
            try:
                self.cursor.execute(sqlstr)
                self.db.commit()
            except Exception as e:
                self.log_msg(flag=self.ERROR, msg_str="获取工字轮信息异常")
            result1 = self.cursor.fetchall()
            gongzilunid = result1[0][1]
            zhongliang = result1[0][2]
            chengzhongtime = result1[0][3]
            zhongliang2 = result1[0][5]
            chengzhongtime2 = result1[0][6]
            # 获取账号信息（登陆账号，登录时间等）
            # 获取固定信息（工厂编号，设备编号。。。。）

    def msg_to_win_thread(self, *args, **kwargs):
        """
        与图形界面进程进行通信，通信类型为消息队列
        :param args:args[0]线程名称，args[1]用于与前端处理程序通信的消息队列
        :param kwargs:
        :return:无
        """
        q = args[1]
        while True:
            if len(self.msg_list) > 0:
                msg = self.msg_list[0]
                if msg["code"] >= self.msg_level and self.msg_level != 6:
                    q.put(msg)
                self.mutex2.acquire()
                self.msg_list.pop(0)
                self.mutex2.release()
            else:
                time.sleep(1)

    def modbus_thread(self, *args, **kwargs):
        """
        与plc通信处理线程，通过检测
        :param args:
        :param kwargs:
        :return:
        """
        while True:
            self.wait_to_connect_plc()  # 等待PLC连接，内部轮询与plc的连接状态，直到成功连接
            while True:
                if not self.is_connect_to_plc():  # 读PLC数据前
                    break
                # 1.扫描信号寄存器
                self.pc_r_coils_block.block_value = self.get_block_values(block_name=self.pc_r_coils_block.block_name,
                                                                          address=self.pc_r_coils_block.start_address,
                                                                          size=self.pc_r_coils_block.size)

                if self.pc_r_coils_block.get_reg_value(self.pc_r_coils_block.regs_name.is_get_weight_first) == 1:
                    # 当值为1时，可以读取第1次称重数据
                    weight_h, weight_l, id_h, id_l = self.get_weight1_and_id()
                    weight = weight_h * 65536 + weight_l
                    spool_id = str(id_h) + str(id_l)
                    load_time_str = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
                    self.into_weight1_date(spool_id, weight, load_time_str)
                    # 处理完成后清除信号
                    self.set_block_values(block_name=self.pc_r_coils_block.block_name,
                                          address=self.pc_r_coils_block.get_reg_address(
                                              self.pc_r_coils_block.regs_name.is_get_weight_first), values=[0, ])

                if self.pc_r_coils_block.get_reg_value(self.pc_r_coils_block.regs_name.is_get_weight_second) == 1:
                    # 当值为1时，可以读取第2次称重数据
                    weight_h, weight_l, id_h, id_l = self.get_weight2_and_id()
                    weight = weight_h * 65536 + weight_l
                    spool_id = str(id_h) + str(id_l)
                    load_time_str = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
                    self.into_weight2_date(spool_id, weight, load_time_str)
                    # 处理完成后，清理信号
                    self.set_block_values(block_name=self.pc_r_coils_block.block_name,
                                          address=self.pc_r_coils_block.get_reg_address(
                                              self.pc_r_coils_block.regs_name.is_get_weight_second), values=[0])

                if self.pc_r_coils_block.get_reg_value(self.pc_r_coils_block.regs_name.is_has_exit_first) == 1:
                    # 当值为1时，通孔有工字轮退出
                    self.pc_r_regs_block.block_value = self.get_block_values(block_name=self.pc_r_regs_block.block_name,
                                                                             address=self.pc_r_regs_block.start_address,
                                                                             size=self.pc_r_regs_block.size)
                    id_h = self.pc_r_regs_block.get_reg_value(reg_name=self.pc_r_regs_block.regs_name.spool_exit1_id_h)
                    id_l = self.pc_r_regs_block.get_reg_value(reg_name=self.pc_r_regs_block.regs_name.spool_exit1_id_l)
                    spool_id = str(id_h) + str(id_l)
                    self.delete_data_by_spool_id(spool_id)  # 根据编号删除退出工字轮的信息
                    self.set_block_values(block_name=self.pc_r_coils_block.block_name,
                                          address=self.pc_r_coils_block.get_reg_address(
                                              self.pc_r_coils_block.regs_name.is_has_exit_first), values=[0, ])

                if self.pc_r_coils_block.get_reg_value(self.pc_r_coils_block.regs_name.is_has_exit_second) == 1:
                    # 当值为1时，第二次称重后有工字轮退出，读取工字轮编号，并删除该条数据
                    self.pc_r_regs_block.block_value = self.get_block_values(block_name=self.pc_r_regs_block.block_name,
                                                                             address=self.pc_r_regs_block.start_address,
                                                                             size=self.pc_r_regs_block.size)
                    id_h = self.pc_r_regs_block.get_reg_value(self.pc_r_regs_block.regs_name.spool_exit2_id_h)
                    id_l = self.pc_r_regs_block.get_reg_value(self.pc_r_regs_block.regs_name.spool_exit2_id_l)
                    spool_id = str(id_h) + str(id_l)
                    self.delete_data_by_spool_id(spool_id)
                    self.set_block_values(block_name=self.pc_r_coils_block.block_name,
                                          address=self.pc_r_coils_block.get_reg_address(
                                              self.pc_r_coils_block.regs_name.is_has_exit_second), values=[0, ])

                if self.pc_r_coils_block.get_reg_value(self.pc_r_coils_block.regs_name.is_has_spool_finished) == 1:
                    # 当值为1是，表示有工字轮已包装完成，通过工字轮编号获取对应数据，将数据打包并发送给miss系统
                    self.pc_r_regs_block.block_value = self.get_block_values(block_name=self.pc_r_regs_block.block_name,
                                                                             address=self.pc_r_regs_block.start_address,
                                                                             size=self.pc_r_regs_block.size)
                    id_h = self.pc_r_regs_block.get_reg_value(self.pc_r_regs_block.regs_name.spool_finished_id_h)
                    id_l = self.pc_r_regs_block.get_reg_value(self.pc_r_regs_block.regs_name.spool_finished_id_l)
                    spool_id = str(id_h) + str(id_l)
                    self.transmit_data_to_miss(spool_id)
                    pass
                time.sleep(0.01)  # 每10毫秒轮询一次

    def log_msg(self, flag, msg_str="", msg_tuple=()):
        """
        打包日志信息
        :param flag:
        :param msg_str:
        :param msg_tuple:
        :return:
        """
        if flag == self.DEBUG:
            if len(msg_str) > 0:
                self.log.debug(msg_str)
            if len(msg_tuple) > 0:
                self.log.debug(msg_tuple)
        elif flag == self.INFO:
            if len(msg_str) > 0:
                self.log.info(msg_str)
            if len(msg_tuple) > 0:
                self.log.info(msg_tuple)
        elif flag == self.WARNING:
            if len(msg_str) > 0:
                self.log.warning(msg_str)
            if len(msg_tuple) > 0:
                self.log.warning(msg_tuple)
        elif flag == self.ERROR:
            if len(msg_str) > 0:
                self.log.error(msg_str)
            if len(msg_tuple) > 0:
                self.log.error(msg_tuple)
        elif flag == self.CRITICAL:
            if len(msg_str) > 0:
                self.log.critical(msg_str)
            if len(msg_tuple) > 0:
                self.log.critical(msg_tuple)
        msg = {
            "code": flag,
            "msgstr": msg_str,
            "msgtuple": msg_tuple
        }
        self.mutex2.acquire()
        self.msg_list.append(msg)
        self.mutex2.release()

    def verify_r_code_to_miss(self):
        """
        与mess系统通信,用于验证二维码信息是否有效，
        :return:
        """
        print(self.scanner_date1)
        ret = int(random.uniform(0, 2))  # 模拟mess系统反馈数据
        if ret == 0:
            self.log.info("二维码验证通过")
            return 0
        elif ret == 1:
            self.log.info("二维码验证未通过")
            return 1
        else:
            print("is a fault")
            return -1

    def transmit_data_to_miss(self, spool_id):
        """
        通过工字轮编号获取工字轮数据，然后将
        :param spool_id:工字轮编号
        :return:
        """
        sql_str = "SELECT * FROM gongzilun WHERE gongzilunid='%s'" % (spool_id,)
        try:
            self.cursor.execute(sql_str)
            self.db.commit()
            result = self.cursor.fetchall()
        except Exception as e:
            self.log_msg(flag=self.ERROR, msg_str="获取包装完成工字轮数据异常")
            return -1
        else:
            if len(result) > 1:
                self.log_msg(flag=self.WARNING, msg_str="工字轮编号有相同的工字轮")
            elif len(result) < 1:
                self.log_msg(flag=self.WARNING, msg_str="未查到相应工字轮数据")
            else:
                data = result[0]
                # 将数据data发送给miss系统的部分代码暂时未编写
            self.log_msg(flag=self.INFO, msg_str="成功将完成的工字轮信息传输到miss系统，ID=%s" % (spool_id,))
        return 0

    def get_weight1_and_id(self):
        """
        通过和PLC通信，获取工字轮第一次称重的重量和ID，
        :return:weight_h、weight_l工字轮重量的高位与低位,id_h、id_l工字轮编号的高位与低位
        """
        self.pc_r_regs_block.block_value = self.get_block_values(block_name=self.pc_r_regs_block.block_name,
                                                                 address=self.pc_r_regs_block.start_address,
                                                                 size=self.pc_r_regs_block.size)
        id_h = self.pc_r_regs_block.get_reg_value(reg_name=self.pc_r_regs_block.regs_name.spool1_id_h)
        id_l = self.pc_r_regs_block.get_reg_value(reg_name=self.pc_r_regs_block.regs_name.spool1_id_l)
        weight_h = self.pc_r_regs_block.get_reg_value(reg_name=self.pc_r_regs_block.regs_name.spool1_weight_h)
        weight_l = self.pc_r_regs_block.get_reg_value(reg_name=self.pc_r_regs_block.regs_name.spool1_weight_l)
        """
        """
        return weight_h, weight_l, id_h, id_l

    def get_weight2_and_id(self):
        """"
        通过和PLC通信，获取工字轮第一次称重的重量和ID，
        :return:weight_h、weight_l工字轮重量的高位与低位,id_h、id_l工字轮编号的高位与低位
        """
        self.pc_r_regs_block.block_value = self.get_block_values(block_name=self.pc_r_regs_block.block_name,
                                                                 address=self.pc_r_regs_block.start_address,
                                                                 size=self.pc_r_regs_block.size)
        id_h = self.pc_r_regs_block.get_reg_value(reg_name=self.pc_r_regs_block.regs_name.spool2_id_h)
        id_l = self.pc_r_regs_block.get_reg_value(reg_name=self.pc_r_regs_block.regs_name.spool2_id_l)
        weight_h = self.pc_r_regs_block.get_reg_value(reg_name=self.pc_r_regs_block.regs_name.spool2_weight_h)
        weight_l = self.pc_r_regs_block.get_reg_value(reg_name=self.pc_r_regs_block.regs_name.spool2_weight_l)
        """
        """
        return weight_h, weight_l, id_h, id_l

    def new_sql_date(self):
        """
        将最新获取的二维码数据（工字轮编号）写入到数据库
        :return:
        """
        gongzilunid = self.scanner_date1
        sqlstr = "INSERT INTO gongzilun (gongzilunid,shifoucheng,zhongliang,chengzhongtime,shifoucheng2) VALUES('%s',1,%f,'%s',0)" % (
            gongzilunid, self.weight_date1, self.weight_time1)
        try:
            self.cursor.execute(sqlstr)
            self.db.commit()
        except Exception as e:
            self.log_msg(flag=self.ERROR, msg_str="数据库添加新工字轮数据失败")
            self.db.rollback()
            return -1
        self.log.info("数据库添加新工字轮数据成功")
        return 0

    def into_weight1_date(self, spool_id, weight, weight_time):
        """
        将第1次称重数据写入到数据库
        :param spool_id: 工字轮编号
        :param weight: 工字轮第一次称重重量
        :param weight_time: 称重时间
        :return:
        """
        sql_str = "UPDATE gongzilun SET shifoucheng1 = 1,zhongliang1=%d,chengzhongtime1='%s' WHERE gongzilunid='%s'" % (
            weight, weight_time, spool_id)
        try:
            self.cursor.execute(sql_str)
            self.db.commit()
        except Exception as e:
            self.log_msg(flag=self.ERROR, msg_str="数据库添加工字轮第一次称重数据更新失败")
            return -1
        self.log_msg(flag=self.INFO, msg_str="数据库添加工字轮第一次称重数据更新成功")
        return 0

    def into_weight2_date(self, spool_id, weight, weight_time):
        """
        将第2次称重数据写入到数据库
        :param spool_id:
        :param weight:
        :param weight_time:
        :return:
        """
        sql_str = "UPDATE gongzilun SET shifoucheng2 = 1,zhongliang2=%d,chengzhongtime2='%s' WHERE gongzilunid='%s'" % (
            weight, weight_time, spool_id)
        try:
            self.cursor.execute(sql_str)
            self.db.commit()
        except Exception as e:
            self.log_msg(flag=self.ERROR, msg_str="数据库添加工字轮第二次称重数据更新失败")
            return -1
        self.log_msg(flag=self.INFO, msg_str="数据库添加工字轮第二次称重数据更新成功")
        return 0

    def delete_data_by_spool_id(self, spool_id):
        """
        根据工字轮编号删除其数据
        :param spool_id: 工字轮编号
        :return:
        """
        sql_str = "DELETE * FROM gongzilun WHERE gongzilunid='%s'" % (spool_id,)
        try:
            self.cursor.execute(sql_str)
            self.db.commit()
        except Exception as e:
            self.log_msg(flag=self.ERROR, msg_str="工字轮数据删除异常")
            return -1
        self.log_msg(flag=self.INFO, msg_str="退出工字轮数据已清除，ID=%s" % (spool_id,))
        return 0

    def init_modbus(self):
        """
        modbus初始化相关代码
        :return:
        """
        self.modbusServer = bzjModbusSlave.bzjModbusSlave()
        self.modbusServer.start()
        self.log.info("建立modbus从站")
        self.log.info("成功创建从站")
        self.log.info("创建寄存器空间，设置初始值")
        self.slave = self.modbusServer.server.add_slave(1)
        self.slave.add_block(block_name="pc_r_regs", block_type=defines.HOLDING_REGISTERS, starting_address=0, size=20)
        self.slave.add_block(block_name="pc_w_regs", block_type=defines.HOLDING_REGISTERS, starting_address=20, size=20)
        self.slave.add_block(block_name="pc_r_coils", block_type=defines.COILS, starting_address=0, size=20)
        self.slave.add_block(block_name="pc_w_coils", block_type=defines.COILS, starting_address=20, size=20)
        self.slave.set_values(block_name="pc_r_regs", address=0,
                              values=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.slave.set_values(block_name="pc_w_regs", address=20,
                              values=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.slave.set_values(block_name="pc_r_coils", address=0,
                              values=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.slave.set_values(block_name="pc_w_coils", address=20,
                              values=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

    def get_block_values(self, block_name, address, size):
        """
        获取modbus寄存器数据
        :param block_name: 寄存器块名称
        :param address: 读寄存器块的起始地址
        :param size: 读取寄存器数据的数量
        :return:
        """
        result = self.slave.get_values(block_name=block_name, address=address, size=size)
        return result

    def set_block_values(self, block_name, address, values):
        """
        向modbus寄存器写入数据
        :param block_name:寄存器块名称
        :param address:写寄存器的起始地址
        :param values:写入寄存器的值，可以是一个list，同时写入到多个连续寄存器中
        :return:
        """
        self.slave.set_values(block_name=block_name, address=address, values=values)

    def destroy_modbus(self):
        """
        程序结束时需要回收modbus相关资源
        :return:
        """
        self.modbusServer.stop()

    def destroy_logger(self):
        """
        程序结束时，要回收logging相关资源
        :return:
        """
        self.log.console.close()

    def is_number(self, num_str):
        """
        判断字符串是否全部由数字组成
        :param num_str:
        :return:
        """
        value = re.compile("^[0-9]+$")
        result = value.match(num_str)
        if result:
            return True
        else:
            return False

    def wait_to_connect_plc(self):
        """
        等待与PLC建立连接，进入循环等待，直到连接成功
        :return:
        """
        self.mutex3.acquire()
        count = 0
        while True:
            # 判断PLC是否已经连接
            connection = len(self.modbusServer.server._sockets)
            self.log_msg(flag=self.INFO, msg_str="等待与PLC建立连接")
            if connection < 2:
                if count % 10 == 0 and count > 0:
                    self.log_msg(flag=self.WARNING, msg_str="与PLC建立连接失败")
                    self.q_err_msg["code"] = 21
                    self.q_err_msg["msgstr"] = "与PLC建立连接失败"
                    self.q_err.put(self.q_err_msg)
                time.sleep(2)
                count += 1
            else:
                self.log_msg(flag=self.INFO, msg_str="成功与PLC已成功建立连接")
                self.q_err_msg["code"] = 20
                self.q_err_msg["msgstr"] = "成功与PLC已成功建立连接"
                self.q_err.put(self.q_err_msg)
                count = 0
                break
            if count > 300:
                self.log_msg(flag=self.WARNING, msg_str="由于长时间无法成功连接PLC，程序无法正常运行，程序进入间歇等待状态")
                time.sleep(30)
                if count > 9000:
                    count = 0
        self.mutex3.release()

    def is_connect_to_plc(self):
        """
        判断pc是否与plc成功建立通信
        :return: 成功返回Ture，失败返回False
        """
        connection = len(self.modbusServer.server._sockets)
        if connection < 2:
            self.log_msg(flag=self.WARNING, msg_str="与PLC连接异常断开")
            self.q_err_msg["code"] = 22
            self.q_err_msg["msgstr"] = "与PLC连接异常断开"
            self.q_err.put(self.q_err_msg)
            return False
        return True

    def run(self, *args, **kwargs):
        """
        后台系统程序初始化，各线程的创建，启动等
        :param args:
        :param kwargs:
        :return:
        """
        self.q = args[0]
        self.q_err = args[1]
        # print(type(self.q_err))
        self.init_modbus()
        self.create_thread()
        self.T3.start()
        self.T4.start()
        self.T5.start()
        self.T6.start()
        self.T3.join()
        self.T4.join()
        self.T5.join()
        self.T6.join()
        self.destroy_modbus()
        self.destroy_logger()


def main(*args, **kwargs):
    bzj = BzjSystem()
    bzj.run(*args, **kwargs)


if __name__ == "__main__":
    main()
    pass
