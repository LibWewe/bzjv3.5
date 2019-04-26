#!usr/bin/env python  
# -*- coding:utf-8 -*-  
""" 
@file: logout.py
@version: v1.0 
@author: WeWe 
@time: 2018/07/23 10:42
@lib v: Python 3.6.4 /2.7.14
@description:This file is fro ...  
"""

import logging
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler
import os
import time
import re


class ConsoleLog(object):
    """
    仅仅是在控制台输出日志信息
    """

    def __init__(self, logName, path, logFilename, logLevel):
        log_file_path = path
        logdir = os.path.join(os.path.curdir, log_file_path)
        if os.path.exists(logdir) == False:
            os.mkdir(logdir)
        file = logFilename
        self.logger = logging.getLogger(logName)  # str: "sys_log"
        self.logger.setLevel(logLevel)  # logging.DEBUG
        # 创建控制台 console handler
        console_handler = logging.StreamHandler()
        # 设置控制台输出时的日志等级
        console_handler.setLevel(logLevel)  # logging.WARNING
        # 创建 formatter
        formatter = logging.Formatter("%(asctime)s :  %(message)s")
        # 添加formatter
        console_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)

    def debug(self, msg_str):
        self.logger.debug(msg_str)

    def info(self, msg_str):
        self.logger.info(msg_str)

    def warning(self, msg_str):
        self.logger.warning(msg_str)

    def error(self, msg_str):
        self.logger.error(msg_str)

    def critical(self, msg_str):
        self.logger.critical(msg_str)


class RotatingFileLog(object):
    """
    在控制台和日志文件中同时输出日志信息，日志文件可以控制日志文件的大小，并产生分日志文件
    """

    def __init__(self, logName, path, logFilename, logLevel):
        log_file_path = path
        logdir = os.path.join(os.path.curdir, log_file_path)
        if os.path.exists(logdir) == False:
            os.mkdir(logdir)

        self.logger = logging.getLogger(logName)  # str: "sys_log"
        self.logger.setLevel(logLevel)  # logging.DEBUG
        # 创建控制台 console handler
        console_handler = logging.StreamHandler()
        # 设置控制台输出时的日志等级
        console_handler.setLevel(logLevel)  # logging.WARNING

        # 创建文件 RotatingFileHandler,最多备份5个日志文件，每个日志文件最大10M =10 * 1024 * 1024
        rotating_file_handler = RotatingFileHandler(filename=log_file_path + logFilename, maxBytes=10*1024,
                                                    backupCount=5, encoding="gbk")
        # 设置写入文件的日志等级
        rotating_file_handler.setLevel(logLevel)  # logging.DEBUG
        # 创建 formatter
        formatter = logging.Formatter("%(asctime)s :  %(message)s")
        # 添加formatter
        console_handler.setFormatter(formatter)
        rotating_file_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)
        self.logger.addHandler(rotating_file_handler)

    def debug(self, msg_str):
        self.logger.debug(msg_str)

    def info(self, msg_str):
        self.logger.info(msg_str)

    def warning(self, msg_str):
        self.logger.warning(msg_str)

    def error(self, msg_str):
        self.logger.error(msg_str)

    def critical(self, msg_str):
        self.logger.critical(msg_str)


class TimedRotatingFileLog(object):
    """
    在控制台和日志文件中同时输出日志信息，日志文件可以按照时间进行创建分日志
    """

    def __init__(self, logName, path, logFilename, logLevel):
        log_file_path = path
        logdir = os.path.join(os.path.curdir, log_file_path)
        if os.path.exists(logdir) == False:
            os.mkdir(logdir)

        self.logger = logging.getLogger(logName)  # str: "sys_log"
        self.logger.setLevel(logLevel)  # logging.DEBUG
        # 创建控制台 console handler
        console_handler = logging.StreamHandler()
        # 设置控制台输出时的日志等级
        console_handler.setLevel(logLevel)  # logging.WARNING

        # 创建TimedRotatingFileHandler,每30秒存在一个文件，最多存在3个文件
        time_rotating_file_handler = TimedRotatingFileHandler(filename=log_file_path + logFilename, when="S",
                                                              interval=30, backupCount=3,encoding="gbk")
        time_rotating_file_handler.suffix = "%Y-%m-%d_%H-%M-%S.log"
        time_rotating_file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}.log$")
        # 每7天存在一个文件，最多存在5个文件
        # time_rotating_file_handler = TimedRotatingFileHandler(filename=log_file_path + logFilename, when="D",
        #                                                       interval=7, backupCount=5)
        # time_rotating_file_handler.suffix="%Y-%m-%d.log"
        # time_rotating_file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}.log$")

        # 设置写入文件的日志等级
        time_rotating_file_handler.setLevel(logLevel)  # logging.DEBUG
        # 创建 formatter
        formatter = logging.Formatter("%(asctime)s :  %(message)s")
        # 添加formatter
        console_handler.setFormatter(formatter)
        time_rotating_file_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)
        self.logger.addHandler(time_rotating_file_handler)

    def debug(self, msg_str):
        self.logger.debug(msg_str)

    def info(self, msg_str):
        self.logger.info(msg_str)

    def warning(self, msg_str):
        self.logger.warning(msg_str)

    def error(self, msg_str):
        self.logger.error(msg_str)

    def critical(self, msg_str):
        self.logger.critical(msg_str)


def main1():
    logger = ConsoleLog(logName="sys_log", path=".\\log\\", logFilename="test1.log", logLevel=logging.DEBUG)
    count = 0
    while True:
        logger.debug("DEBUG")
        logger.info("INFO")
        logger.warning("WARNING")
        logger.error("ERROR")
        logger.critical("CRITICAL")
        count += 1
        time.sleep(0.2)


def main2():
    logger = RotatingFileLog(logName="sys_log", path=".\\log\\", logFilename="test2.log", logLevel=logging.DEBUG)
    count = 0
    while True:
        logger.debug("DEBUG")
        logger.info("INFO")
        logger.warning("WARNING")
        logger.error("ERROR")
        logger.critical("CRITICAL")
        count += 1
        time.sleep(0.2)


def main3():
    logger = TimedRotatingFileLog(logName="sys_log", path=".\\log\\", logFilename="test3.log", logLevel=logging.DEBUG)
    count = 0
    while True:
        logger.debug("DEBUG")
        logger.info("INFO")
        logger.warning("WARNING")
        logger.error("ERROR")
        logger.critical("CRITICAL")
        count += 1
        time.sleep(0.5)


if __name__ == "__main__":
    main1()
    pass
