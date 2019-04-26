#!usr/bin/env python  
# -*- coding:utf-8 -*-  
""" 
@file: config.py
@version: v1.0 
@author: WeWe 
@time: 2018/07/18 11:33
@lib v: Python 3.6.4 /2.7.14
@description:This file is fro ...  
"""

import os
import re
import json

BASE_DIRS = os.path.dirname(__file__)


# 数据库配置
class config(object):
    def __init__(self):
        super(config, self).__init__()
        self.mysql = {
            "host": "localhost",
            "user": "root",
            "passwd": "mysql20180223%",
            "dbName": "bzj1",
            "admin_field": ["id", "uname", "upwd"],
            "gongzilun_field": ["id", "gongzilunid", "zhongliang", "chengzhongtime",
                                "shifoucheng2", "zhongliang2", "chengzhongtime2", "gongzilunno"],
            "lineuser_field": ["id", "uname", "upwd", "denglushijian", "runnormal"],
            "login_field": ["id", "uname", "upwd"],
            "machine_field": ["id", "shebeiid", "gongchangid", "gongxuid", "caijidianid", "caijidiantype", "banci",
                              "denglushijian"]
        }

        self.scanner = {
            "s1_ip": "192.168.1.68",  # "192.168.8.51"
            "s1_port": 8080,
            "s2_ip": "192.168.1.68",
            "s2_port": 8081,
        }

        self.level = {
            "msg_level": 0,  # 0:没有设置；1：DEBUG；2：INFO；3:WARNING；4：ERROR；5：CRITICAL；6：NONE
        }

        self.sel = {  # 扫码枪串口通讯配置
            "selComPort": "COM1",
            "selBaudRate": 9600,
        }

    def cofig_update(self):
        """
        读取配置文件，获取配置参数，配置参数总共有11个，
        没有写的使用默认设置，默认值为上面的字典参数

        注意：当涉及到目录时，以main所在目录为当前目录
        :return:
        """
        if os.path.exists(".\\config\\") == False:
            os.mkdir(".\\config\\")
        if os.path.exists(".\\config\\config") == False:
            with open(".\\config\\config", "w+") as file:
                file.write("")
            return
        with open(".\\config\\config", "r") as file:
            text = file.readlines()
            for line in text:
                if re.match("mysql_host=", line):
                    host = line[line.index("=") + 1:]
                    self.mysql["host"] = host[0:len(host) - 1]
                if re.match("mysql_user", line):
                    user = line[line.index("=") + 1:]
                    self.mysql["user"] = user[0:len(user) - 1]
                if re.match("mysql_pwd", line):
                    pwd = line[line.index("=") + 1:]
                    self.mysql["passwd"] = pwd[0:len(pwd) - 1]
                if re.match("dbName", line):
                    dbName = line[line.index("=") + 1:]
                    self.mysql["dbName"] = dbName[0:len(dbName) - 1]
                if re.match("s1_ip", line):
                    s1_ip = line[line.index("=") + 1:]
                    self.scanner["s1_ip"] = s1_ip[0:len(s1_ip) - 1]
                if re.match("s1_port", line):
                    s1_port = line[line.index("=") + 1:]
                    self.scanner["s1_port"] = int(s1_port[0:len(s1_port) - 1])
                if re.match("s2_ip", line):
                    s2_ip = line[line.index("=") + 1:]
                    self.scanner["s2_ip"] = s2_ip[0:len(s2_ip) - 1]
                if re.match("s2_port", line):
                    s2_port = line[line.index("=") + 1:]
                    self.scanner["s2_port"] = int(s2_port[0:len(s2_port) - 1])
                if re.match("msg_level", line):
                    msg_level = line[line.index("=") + 1:]
                    if msg_level[0:len(msg_level) - 1] == "DEBUG":
                        self.level["msg_level"] = 1
                    if msg_level[0:len(msg_level) - 1] == "INFO":
                        self.level["msg_level"] = 2
                    if msg_level[0:len(msg_level) - 1] == "WARNING":
                        self.level["msg_level"] = 3
                    if msg_level[0:len(msg_level) - 1] == "ERROR":
                        self.level["msg_level"] = 4
                    if msg_level[0:len(msg_level) - 1] == "CRITICAL":
                        self.level["msg_level"] = 5
                    if msg_level[0:len(msg_level) - 1] == "NONE":
                        self.level["msg_level"] = 6
                if re.match("selComPort", line):
                    selComPort = line[line.index("=") + 1:]
                    self.sel["selComPort"] = selComPort[0:len(selComPort) - 1]
                if re.match("selBaudRate", line):
                    selBaudRate = line[line.index("=") + 1:]
                    self.sel["selBaudRate"] = int(selBaudRate[0:len(selBaudRate) - 1])

    def get_config(self):
        """
        读取json文件中的数据
        :return:
        """
        if os.path.exists(".\\config\\") == False:
            os.mkdir(".\\config\\")
        if os.path.exists(".\\config\\config.json") == False:
            with open(".\\config\\config.json", "w+") as file:
                file.write("")
            return
        try:
            json_data = open(".\\config\\config.json").read()
            cfg_data = json.loads(json_data)
        except Exception as e:
            print(e, "读取配置数据异常")
            return
        if "mysql_host" in cfg_data[0]:
            self.mysql["host"] = cfg_data[0]["mysql_host"]
        if "mysql_user" in cfg_data[0]:
            self.mysql["user"] = cfg_data[0]["mysql_user"]
        if "mysql_pwd" in cfg_data[0]:
            self.mysql["passwd"] = cfg_data[0]["mysql_pwd"]
        if "dbName" in cfg_data[0]:
            self.mysql["dbName"] = cfg_data[0]["dbName"]
        if "s1_ip" in cfg_data[0]:
            self.scanner["s1_ip"] = cfg_data[0]["s1_ip"]
        if "s1_port" in cfg_data[0]:
            self.scanner["s1_port"] = cfg_data[0]["s1_port"]
        if "s2_ip" in cfg_data[0]:
            self.scanner["s2_ip"] = cfg_data[0]["s2_ip"]
        if "s2_port" in cfg_data[0]:
            self.scanner["s2_port"] = cfg_data[0]["s2_port"]
        if "msg_level" in cfg_data[0]:
            if cfg_data[0]["msg_level"] == "DEBUG":
                self.level["msg_level"] = 1
            elif cfg_data[0]["msg_level"] == "INFO":
                self.level["msg_level"] = 2
            elif cfg_data[0]["msg_level"] == "WARNING":
                self.level["msg_level"] = 3
            elif cfg_data[0]["msg_level"] == "ERROR":
                self.level["msg_level"] = 4
            elif cfg_data[0]["msg_level"] == "CRITICAL":
                self.level["msg_level"] = 5
            else:
                self.level["msg_level"] = 2

        if "selComPort" in cfg_data[0]:
            self.sel["selComPort"] = cfg_data[0]["selComPort"]
        if "selBaudRate" in cfg_data[0]:
            self.sel["selBaudRate"] = cfg_data[0]["selBaudRate"]


# 2个扫码枪ip，port

def main():
    cfg_test = config()
    print(cfg_test.sel["selComPort"])
    cfg_test.get_config()
    print(cfg_test.sel["selComPort"])
    pass


if __name__ == '__main__':
    main()
    pass
