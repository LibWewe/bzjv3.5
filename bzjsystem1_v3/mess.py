#!usr/bin/env python  
# -*- coding:utf-8 -*-  
""" 
@file: mess.py
@version: v1.0 
@author: WeWe 
@time: 2018/07/24 17:19
@lib v: Python 3.6.4 /2.7.14
@description:This file is fro ...  
"""

import urllib.request
import urllib.parse
import json
import http.cookiejar
import time

headerstr = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json;charset=UTF-8'
}


class httpForMess(object):
    def __init__(self):
        """
        cookies_filename:将获取的cookie存入到本地文件
        """
        self.cookies_filename = "cookies.py"
        self.url = 'http://192.168.1.10'  # mess系统接口IP
        self.cookies = http.cookiejar.MozillaCookieJar(self.cookies_filename)
        self.handler = urllib.request.HTTPCookieProcessor(self.cookies)
        self.opener = urllib.request.build_opener(self.handler)
        self.message = ""

    def tranceRcode(self, data):
        """
        给mess系统发送二维码数据
        :param data: json数据，用于给
        :return:
        """
        json_str = json.dumps(data).encode("utf-8")
        url = self.url + '/****'
        req = urllib.request.Request(url=url, data=json_str, headers=headerstr)
        try:
            res = self.opener.open(req)
            jsoncode = json.load(res)
            self.cookies.save(ignore_discard=True, ignore_expires=True)
            for item in self.cookies:
                print('Name = ' + item.name)
                print('Value = ' + item.value)
        except Exception as e:
            print("================login err=====================")
            print(e)
            print("==============================================")
            return -2
        if jsoncode["code"] != 0:
            self.message = jsoncode["message"]
            return jsoncode["code"]
        return 0


def main():
    """

    :return:
    """
    mess = httpForMess()
    mess.login("jslfscz", "123456")


if __name__ == "__main__":
    main()
    pass
