#!usr/bin/env python  
# -*- coding:utf-8 -*-  
""" 
@file: bzj.py
@version: v1.0 
@author: WeWe 
@time: 2018/07/26 12:48
@lib v: Python 3.6.4 /2.7.14
@description:This file is fro ...
"""

from bzjsystem1_v3 import bzj_sys as bzjsys
from bzjWinv1 import bzj_win as bzjwin
from multiprocessing import Process, freeze_support, Queue
import os
import win32con, win32api
import psutil

"""
pyinstaller -w -p F:\study\python\virtualenv\bzjpy3 bzj.py
"""


def get_process_count(imagename):
    p = os.popen('tasklist /FI "IMAGENAME eq %s"' % imagename)
    return p.read().count(imagename)


def jsjsystem(*args, **kwargs):
    bzjsys.main(*args, **kwargs)


def jsjwin(*args, **kwargs):
    bzjwin.main(*args, **kwargs)


def main():
    freeze_support()
    pid = os.getpid()
    p0 = psutil.Process(pid=pid)
    # # 判断程序名称是否被修改，被修改则无法正常运行
    # if p0.name() != "bzj.exe":
    #     if win32api.MessageBox(0, "软件名称被恶意修改，程序无法正常运行，请改为 bzj.exe", "提示",
    #                            win32con.MB_OK | win32con.MB_ICONWARNING) == win32con.MB_OKCANCEL:
    #         return
    # # 根据程序名称，判断程序是否已启动，若已启动则无法再次运行
    # if get_process_count("bzj.exe") >= 3:
    #     if win32api.MessageBox(0, "软件已运行，无法重新启动", "提示",
    #                            win32con.MB_OK | win32con.MB_ICONWARNING) == win32con.MB_OKCANCEL:
    #         return
    queue = Queue(maxsize=20)
    q_err = Queue(maxsize=20)
    p1 = Process(target=jsjwin, name="jsjwin", args=(queue, q_err), kwargs={})
    p2 = Process(target=jsjsystem, name="jsjsystem", args=(queue, q_err), kwargs={})
    p1.start()
    p2.start()
    p1.join()
    if p1.is_alive() == False:
        p2.terminate()
    p2.join()


if __name__ == "__main__":
    main()
    pass
