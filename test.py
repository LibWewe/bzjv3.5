#!usr/bin/env python  
# -*- coding:utf-8 -*-  
""" 
@file: test.py
@version: v1.0 
@author: WeWe 
@time: 2018/07/27 9:21
@lib v: Python 3.6.4 /2.7.14
@description:This file is fro
"""
import random
import threading
import time
import os
import re
import subprocess
import serial


def append_list(*args, **kwargs):
    mutex = args[0]
    list = args[1]
    for i in range(0, 100):
        stime = int(random.uniform(1, 4))
        mutex.acquire()
        list.append(i)
        mutex.release()
        time.sleep(stime)


def pop_list(*args, **kwargs):
    mutex = args[0]
    list = args[1]
    for i in range(0, 100):
        stime = int(random.uniform(3, 6))
        if len(list) > 0:
            mutex.acquire()
            print("list[0] =", list[0])
            list.pop(0)
            mutex.release()
        time.sleep(stime)


def main1():
    """
    测试线程互斥锁
    :return:
    """
    mutex = threading.Lock()
    list = []
    t1 = threading.Thread(target=append_list, args=(mutex, list,), kwargs={})
    t2 = threading.Thread(target=pop_list, args=(mutex, list,), kwargs={})
    t1.start()
    t2.start()
    while True:
        cmd = input(">>> ")
        if cmd == "q":
            break
        print(list)
    t1.join()
    t2.join()


def get_process_count(imagename):
    p = os.popen('tasklist /FI "IMAGENAME eq %s"' % imagename)
    return p.read().count(imagename)


def timer_start():
    t = threading.Timer(120, watch_func, ("is running..."))
    t.start()


def watch_func(msg):
    print("I'm watch_func,", msg)
    if get_process_count('main.exe') == 0:
        print(subprocess.Popen([r'D:\shuaji\bin\main.exe']))
    timer_start()


def main2():
    """
    测试定时器，及其回调函数
    :return:
    """
    timer_start()
    while True:
        time.sleep(1)


def is_number(num_str):
    """
    判断字符串是否全为数字
    :param num_str:
    :return:
    """
    value = re.compile("^[0-9]+$")
    result = value.match(num_str)
    if result:
        return True
    else:
        return False


def usb_read(ser):
    a = 0
    while True:
        try:
            # rcv = ser.read_all().decode("GBK")
            rcv = ser.readline().decode("gbk")
        except Exception as e:
            print(e)
        else:
            if rcv is not "":
                if len(rcv) < 22:
                    print("failed")
                else:
                    rcv1 = rcv[:-2]
                    if is_number(rcv1):
                        print(rcv1 + "  " + str(a))
                        a += 1
                    else:
                        print("failed ", rcv1)
        time.sleep(0.1)


def usb_write(ser):
    while True:
        try:
            ser.write("同力智能\n".encode("gbk"))
        except Exception as e:
            print(e)
        time.sleep(1)


def main3():
    """
    模拟串口通讯
    :return:
    """
    try:
        ser = serial.Serial("COM2", 9600, timeout=None)
        print(ser.name)
    except Exception as e:
        print(e, type(e))
    else:
        t1 = threading.Thread(target=usb_read, args=(ser,), kwargs={})
        t2 = threading.Thread(target=usb_write, args=(ser,), kwargs={})
        t1.start()
        t2.start()
        t1.join()
        t2.join()


def rcode_simple():
    """
    二维码
    :return:
    """
    import qrcode
    # img = qrcode.make("1501020800061803170020")  # https://bbs.csdn.net/topics/390937465
    img = qrcode.make("http://code.py40.com/pyqt5/16.html")
    # img = qrcode.make("轮号：7083   机台：10-28\n时间：09:22   班次：甲班")
    img.save("151.png")


def rcode_part(text):
    """

    :param text:
    :return:
    """
    import qrcode
    qr = qrcode.QRCode(version=2,
                       error_correction=qrcode.ERROR_CORRECT_L,
                       box_size=2,
                       border=1
                       )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image()
    img.save("160.png")


def main4():
    """
    测试二维码
    :return:
    """
    rcode_simple()
    # rcode_part("1501020800061803170020")
    pass



if __name__ == "__main__":
    main3()
    pass
