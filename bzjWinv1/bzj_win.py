#!usr/bin/env python  
# -*- coding:utf-8 -*-  
""" 
@file: bzj.py
@version: v1.0 
@author: WeWe 
@time: 2018/07/18 11:19
@lib v: Python 3.6.4 /2.7.14
@description:This file is fro ...  
"""
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QComboBox, QTableWidgetItem, QStyle
from PyQt5.QtGui import QResizeEvent, QCloseEvent, QMouseEvent, QRegExpValidator, QStandardItemModel, QStandardItem, \
    QIcon
from PyQt5.QtCore import QSize, QRect, Qt, QTimer, QRegExp, QPoint, QThread, QMutex, QModelIndex, QVariant, QObject
from bzjWinv1 import loginWin
from bzjWinv1 import mainWin
from bzjWinv1 import changePwdWin
from bzjWinv1 import logMsgWin
from config import config
from bzjWinv1 import logout
from hashlib import sha1
import pymysql
import sys
import time
import math
import threading
import gc
import logging


class loginView(QtWidgets.QDialog, loginWin.Ui_Form):
    def __init__(self):
        """
        登陆界面初始化
        """
        super(loginView, self).__init__()
        self.setupUi(self)
        self.account.setPlaceholderText("用户名")
        self.password.setPlaceholderText("密  码")
        self.setWhatsThis("登陆包装机显示界面")


class changePwdView(QtWidgets.QDialog, changePwdWin.Ui_Form):
    def __init__(self):
        """
        修改密码界面初始化
        """
        super(changePwdView, self).__init__()
        self.setupUi(self)
        self.oldPwd.setPlaceholderText("请输入原始密码")
        self.newPwd1.setPlaceholderText("请输入新密码")
        self.newPwd2.setPlaceholderText("请再次输入新密码")
        self.setWhatsThis("")


class logMsgView(QtWidgets.QDialog, logMsgWin.Ui_Form):
    def __init__(self):
        """
        日志信息界面
        """
        super(logMsgView, self).__init__()
        self.setupUi(self)


class get_msg_from_sys_thread(QThread):
    def __init__(self, win):
        """
        接收后台程序信息线程初始化
        :param win:
        """
        super(get_msg_from_sys_thread, self).__init__()
        self.win = win
        self.q = self.win.q
        self.list = self.win.msg_list
        self.mutex = self.win.mutex1
        self.msg_append = self.win.msg_append
        self.isStart = False

    def run(self):
        """
        线程主程序
        :return:
        """
        while self.isStart:
            if not self.q.empty():
                msg = self.q.get()
                self.msg_append(msg)
            else:
                time.sleep(1)


class set_status_msg_thread(QThread):
    def __init__(self, win):
        """
        处理状态栏信息线程
        :param win:
        """
        super(set_status_msg_thread, self).__init__()
        self.win = win
        self.status_lable = self.win.statuLable
        self.mutex1 = self.win.mutex1
        self.list = self.win.msg_list
        self.signal = self.win.signal
        self.log_msg = self.win.log_msg

    def run(self):
        """
        线程主程序
        :return:
        """
        while True:
            try:
                self.signal.wait()
                self.signal.clear()
            except Exception as e:
                self.log_msg(flag=4, msg_str="程序异常", msg_tuple=e)
            if len(self.list) > 0:
                msg_str = ""
                if len(self.list[0]["msgstr"]) > 0:
                    msg_str = self.list[0]["msgstr"]
                if self.list[0]["msgtuple"]:
                    for i in self.list[0]["msgtuple"].args:
                        msg_str += str(i) + "，"
                self.status_lable.setText(msg_str)
                self.mutex1.lock()
                self.list.pop(0)
                self.mutex1.unlock()
            # else:
            #     time.sleep(1)


class get_err_msg_from_sys_thread(QThread):

    signal = QtCore.pyqtSignal(dict)

    def __init__(self, win, q_err):
        """
        后台异常处理线程
        :param win:
        :param q_err:
        """
        super(get_err_msg_from_sys_thread, self).__init__()
        self.win = win
        self.q_err = q_err
        self.isStart = False
        # print(type(self.q_err))

    def run(self):
        """
        线程主程序
        :return:
        """
        while self.isStart:
            if not self.q_err.empty():
                msg = self.q_err.get()
                # print(type(msg), msg)
                self.signal.emit(msg)
            time.sleep(1)


class mainView(QtWidgets.QMainWindow, mainWin.Ui_MainWindow):
    """
    主窗口类
    """

    def __init__(self):
        super(mainView, self).__init__()
        self.setupUi(self)
        # 主要变量初始化
        self.isShow_flag = False
        self.account = "admin"
        self.password = "456789"
        self.loadTimeStr = ""
        self.isAdmin = False
        self.curPage = 1
        self.totalPage = 1

        # 日志相关变量和类的初始化
        # self.log = logout.TimedRotatingFileLog("win_log",".\\log\\", "win.log",logging.DEBUG)
        self.log = logout.RotatingFileLog("win_log", ".\\log\\", "win.log", logging.DEBUG)
        self.msg_list = []
        self.msg_list2 = []
        self.DEBUG = 1
        self.INFO = 2
        self.WARNING = 3
        self.ERROR = 4
        self.CRITICAL = 5

        # 线程锁及线程信号量初始化
        self.mutex1 = QMutex()
        self.mutex2 = QMutex()
        self.signal = threading.Event()
        self.signal.clear()

        # 初始化数据库相关信息
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

        # self.db = pymysql.Connect(mysql["host"], mysql["user"], mysql["passwd"], mysql["dbName"])
        # self.cursor = self.db.cursor()

        # 系统时间显示相关类初始化
        self.updateTime = QTimer()
        self.updateTime.start(1000)
        self.updateTime.timeout.connect(self.updateTimeShow)

        # 自动刷新显示列表定时器初始化
        self.Refresh_timer = QTimer()
        self.Refresh_timer.timeout.connect(self.refreshSelf)

        # 扫码枪未连接提示
        self.scanner_statue_timer = QTimer()
        self.scanner_statue_timer.timeout.connect(self.scanner_statu_change)
        self.scanner_statue_flag = False

        # PLC未连接提示
        self.plc_statue_timer = QTimer()
        self.plc_statue_timer.timeout.connect(self.plc_statue_change)
        self.plc_statue_flag = False

        # 初始化状态栏及时间栏相关类及变量初始化
        # self.setWhatsThis("123456789")
        self.statuLable = QtWidgets.QLabel()
        # self.errLable = QtWidgets.QLabel()
        self.nowTimeLable = QtWidgets.QLabel()
        self.statuLable.setAlignment(Qt.AlignLeft)
        # self.errLable.setAlignment(Qt.AlignCenter)
        self.nowTimeLable.setAlignment(Qt.AlignRight)
        self.statusbar.addWidget(self.statuLable)
        # self.statusbar.addWidget(self.errLable)
        self.statusbar.addWidget(self.nowTimeLable)
        self.statusbar.setStyleSheet("QStatusBar::item{border: 0px}")
        self.statuLable.setText("就绪")
        # self.errLable.setStyleSheet("color:red;font:bold;font-size:12px")
        # self.errLable.setText("异常显示")
        nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        self.nowTimeLable.setText(str(nowtime))
        self.nowTimeLable.setStyleSheet("color:blue;font-size:12px")
        self.statuLable.setStyleSheet("color:red;font-size:12px")

        # 用户及登陆信息栏初始化
        self.textLable.setStyleSheet("color:blue;font:bold;font-size:14px")
        self.userLable.setStyleSheet("color:red;font:bold;font-size:14px")
        self.loadTimeLable2.setStyleSheet("color:red;font:bold;font-size:14px")

        # 设置设置信息为只读
        self.machineID.setReadOnly(True)
        self.plantID.setReadOnly(True)
        self.processNo.setReadOnly(True)
        self.localityNo.setReadOnly(True)
        self.type.setReadOnly(True)
        self.loadTime.setReadOnly(True)
        self.classBox.setEnabled(False)

        # 初始化页码显示控件
        self.curPageNoEdit.setMaximumSize(QSize(40, 20))
        self.curPageNoEdit.setStyleSheet("color:blue;font:bold;font-size:14px")
        validator = QRegExpValidator(QRegExp("\d+"))
        self.curPageNoEdit.setValidator(validator)  # 设置只能输入数字
        self.curPageNoEdit.setText(str(self.curPage))
        self.curPageNoEdit.setAlignment(Qt.AlignCenter)
        self.totalPageLable.setStyleSheet("color:blue;font:bold;font-size:14px")

        # 设置PLC和扫码枪连接状态
        self.PlcConStatu.setText("PLC等待连接")
        self.ScanConStatu.setText("扫码枪等待连接")
        self.PlcConStatu.setStyleSheet("background:none;border:none;font:bold;font-size:12px;color:#FF8800")
        self.ScanConStatu.setStyleSheet("background:none;border:none;font:bold;font-size:12px;color:#FF8800")

        # 设置各类信号与槽
        self.prevPageBtn.clicked.connect(self.onClickedPrevPageBtn)
        self.nextPageBtn.clicked.connect(self.onClickedNextPageBtn)
        self.curPageNoEdit.returnPressed.connect(self.onPressedCurPageNoEdit)

        self.setBtn.clicked.connect(self.onClickedSetBtn)
        self.changePwdBtn.clicked.connect(self.onClickedChangePwdBtn)
        self.refreshBtn.clicked.connect(self.onClickedRefreshBtn)
        self.refreshSelfBtn.clicked.connect(self.onClickedRefreshSelfBtn)

        # 设置显示列表
        # self.showTable.setHorizontalHeaderLabels(["序号", "工字轮编号", "重量1", "称重时间1", "是否二次称重", "重量2", "称重时间2"])
        self.mode = QStandardItemModel()
        self.mode.setRowCount(15)
        self.mode.setColumnCount(7)
        for i in range(0, 15):
            for j in range(0, 7):
                self.mode.setItem(i, j, QStandardItem(""))
        self.mode.setHorizontalHeaderLabels(["序号", "工字轮编号", "重量1", "称重时间1", "是否二次称重", "重量2", "称重时间2"])
        self.showTable.setModel(self.mode)
        self.showTable.verticalHeader().setVisible(False)
        self.setTable()

        # 初始化登陆界面类
        self.loginView = loginView()
        self.loginView.loginBtn.clicked.connect(self.onClickedLoginBtn)
        self.loginView.loginBtn.pressed.connect(self.onClickedLoginBtn)
        self.loginView.account.returnPressed.connect(self.onClickedLoginBtn)
        self.loginView.password.returnPressed.connect(self.onClickedLoginBtn)

        # 初始化修改密码界面类
        self.changePwdView = changePwdView()
        self.changePwdView.changeBtn.clicked.connect(self.onClickedChangeBtn_c)
        self.changePwdView.changeBtn.pressed.connect(self.onClickedChangeBtn_c)
        self.changePwdView.oldPwd.returnPressed.connect(self.onClickedChangeBtn_c)
        self.changePwdView.newPwd1.returnPressed.connect(self.onClickedChangeBtn_c)
        self.changePwdView.newPwd2.returnPressed.connect(self.onClickedChangeBtn_c)

        self.logMsgView = logMsgView()

    def updateTimeShow(self):
        """
        系统时间显示程序
        :return:
        """
        nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        self.nowTimeLable.setText(str(nowtime))

    def loginShow(self):
        """
        登陆界面显示
        :return:
        """
        self.log_msg(flag=self.INFO, msg_str="启动登陆程序")
        self.loginView.show()
        self.loginView.account.setText(self.account)
        self.loginView.password.setText(self.password)

    def changePwdShow(self):
        """
        修改密码界面显示
        :return:
        """
        self.changePwdView.show()
        if self.isAdmin == True:
            self.changePwdView.setWindowTitle("系统设置")
        else:
            self.changePwdView.setWindowTitle("修改密码")
        self.changePwdView.oldPwd.setText("")
        self.changePwdView.newPwd1.setText("")
        self.changePwdView.newPwd2.setText("")

    def mainWinShow(self):
        """
        主界面显示
        :return:
        """
        self.userLable.setText(self.account)
        nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        self.loadTimeLable2.setText(str(nowtime))
        self.show()
        ret = self.getSpoolDate(pageNo=self.curPage)
        if ret == -1:
            return
        else:
            self.updateTable()
        ret = self.getTotalPage()
        if ret == -1:
            return
        else:
            self.totalPageLable.setText("/%d(共%d页)" % (self.totalPage, self.totalPage))
        ret = self.updateOnlineDate()
        if ret == -1:
            return
        self.getMachineSetDate()
        if self.isAdmin == True:
            self.changePwdBtn.setText("系统设置")
            QMessageBox.information(self, "提示", "管理员账户验证成功！         ", QMessageBox.Ok,
                                    QMessageBox.Ok)
            self.log_msg(flag=self.INFO, msg_str="管理员账户验证成功")
        self.T3.isStart = True
        self.T3.start()

    def verfiyAdmin(self):
        """
        确认登陆账号是否为管理员账号
        :return:
        """
        sqlStr = "SELECT * FROM adminuser WHERE uname = '%s'" % self.account
        try:
            self.cursor.execute(sqlStr)
            self.db.commit()
        except Exception as e:
            self.log_msg(flag=self.ERROR, msg_str="数据异常请重新再试", msg_tuple=e)
            return -1
        result = self.cursor.fetchall()
        if len(result) > 0:
            self.isAdmin = True
        else:
            self.isAdmin = False
        return 0

    def onClickedLoginBtn(self):
        """
        确认登陆处理
        :return:
        """
        self.account = self.loginView.account.text()
        self.password = self.loginView.password.text()
        if self.account == "" or self.password == "":
            QMessageBox.warning(self, "提示", "用户名或密码不能为空！         ", QMessageBox.Ok,
                                QMessageBox.Ok)
            return
        sqlstr = "SELECT * FROM login WHERE uname = '%s'" % self.account
        try:
            self.cursor.execute(sqlstr)
            self.db.commit()
        except Exception as e:
            self.log_msg(flag=self.ERROR, msg_tuple=e)
            return
        result = self.cursor.fetchall()
        if len(result) == 0:
            QMessageBox.warning(self, "提示", "该用户名不存在！         ", QMessageBox.Ok,
                                QMessageBox.Ok)
            return
        s1 = sha1(self.password.encode("utf-8"))
        pwd = s1.hexdigest()
        if result[0][2] == pwd:
            self.loadTimeStr = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
            self.loginView.close()
            ret = self.verfiyAdmin()
            if ret == -1:
                return
            else:
                self.mainWinShow()
                self.log_msg(flag=self.INFO, msg_str="%s账号登陆成功" % self.account)
        else:
            QMessageBox.warning(self, "提示", "密码错误！         ", QMessageBox.Ok,
                                QMessageBox.Ok)

    def onClickedPrevPageBtn(self):
        """
        点击上一页处理
        :return:
        """
        self.log_msg(flag=self.INFO, msg_str="查看上一页")
        if self.curPage == 1:
            return
        elif self.curPage > 1:
            ret = self.getSpoolDate(pageNo=self.curPage - 1)
            if ret == 0:
                self.updateTable()
                self.curPage -= 1
                self.curPageNoEdit.setText(str(self.curPage))
            else:
                return

    def onClickedNextPageBtn(self):
        """
        点击下一页处理
        :return:
        """
        self.log_msg(flag=self.INFO, msg_str="查看下一页")
        self.getTotalPage()
        self.totalPageLable.setText("/%d(共%d页)" % (self.totalPage, self.totalPage))
        if self.curPage == self.totalPage:
            return
        elif self.curPage < self.totalPage:
            ret = self.getSpoolDate(pageNo=self.curPage + 1)
            if ret == 0:
                self.updateTable()
                self.curPage += 1
                self.curPageNoEdit.setText(str(self.curPage))
            else:
                return

    def onPressedCurPageNoEdit(self):
        """
        enter键当前页码框处理
        :return:
        """
        ret = self.getTotalPage()
        if ret == -1:
            return
        else:
            self.totalPageLable.setText("/%d(共%d页)" % (self.totalPage, self.totalPage))
        pageNo = int(self.curPageNoEdit.text())
        if pageNo == self.curPage:
            self.onClickedRefreshBtn()
        if pageNo < 1:
            pageNo = 1
        elif pageNo <= self.totalPage:
            pageNo = pageNo
        else:
            pageNo = self.totalPage
        ret = self.getSpoolDate(pageNo=pageNo)
        if ret == 0:
            self.updateTable()
            self.curPage = pageNo
            self.curPageNoEdit.setText(str(self.curPage))
            self.log_msg(flag=self.INFO, msg_str="查看第 %d 页" % self.curPage)

    def onClickedSetBtn(self):
        """
        处理点击设置按钮程序
        :return:
        """
        btnStr = self.setBtn.text()
        if btnStr == "编   辑":
            self.log_msg(flag=self.INFO, msg_str="编辑......")
            if self.isAdmin == True:
                self.machineID.setReadOnly(False)
                self.plantID.setReadOnly(False)
                self.processNo.setReadOnly(False)
                self.localityNo.setReadOnly(False)
                self.type.setReadOnly(False)
                self.classBox.setEnabled(True)
            else:
                self.classBox.setEnabled(True)
            self.setBtn.setText("保   存")
            self.changSetBoxColor("red")

        if btnStr == "保   存":
            if self.isAdmin == True:
                self.machineID.setReadOnly(True)
                self.plantID.setReadOnly(True)
                self.processNo.setReadOnly(True)
                self.localityNo.setReadOnly(True)
                self.type.setReadOnly(True)
                self.classBox.setEnabled(False)
            else:
                self.classBox.setEnabled(False)
            ret = self.updataMachineSetDate()
            if ret == 0:
                self.log_msg(flag=self.INFO, msg_str="保存成功")
                self.setBtn.setText("编   辑")
                self.changSetBoxColor("black")

    def onClickedChangePwdBtn(self):
        """
        点击系统设置按钮处理程序
        :return:
        """
        self.changePwdShow()
        self.hide()
        self.changePwdView.exec()
        self.show()

    def onClickedRefreshBtn(self):
        """
        点击刷新按钮处理程序
        :return:
        """
        ret = self.getSpoolDate(pageNo=self.curPage)
        if ret == -1:
            return
        self.updateTable()
        ret = self.getTotalPage()
        if ret == -1:
            return
        else:
            self.totalPageLable.setText("/%d(共%d页)" % (self.totalPage, self.totalPage))
        self.setTable()
        self.log_msg(flag=self.INFO, msg_str="当前页刷新成功")

    def onClickedRefreshSelfBtn(self):
        """
        点击自动刷新按钮
        :return:
        """
        btnStr = self.refreshSelfBtn.text()
        if btnStr == "自动刷新":
            self.refreshSelfBtn.setText("停止刷新")
            self.Refresh_timer.start(1000)
            self.setBtn.setEnabled(False)
            self.refreshBtn.setEnabled(False)
            self.changePwdBtn.setEnabled(False)
            self.prevPageBtn.setEnabled(False)
            self.nextPageBtn.setEnabled(False)
            self.curPageNoEdit.setEnabled(False)
        if btnStr == "停止刷新":
            self.refreshSelfBtn.setText("自动刷新")
            self.Refresh_timer.stop()
            self.setBtn.setEnabled(True)
            self.refreshBtn.setEnabled(True)
            self.changePwdBtn.setEnabled(True)
            self.prevPageBtn.setEnabled(True)
            self.nextPageBtn.setEnabled(True)
            self.curPageNoEdit.setEnabled(True)
            self.log_msg(flag=self.INFO, msg_str="停止自动刷新")

    def onClickedChangeBtn_c(self):
        """
        点击确认修改程序
        :return:
        """
        oldPwd = self.changePwdView.oldPwd.text()
        newPwd1 = self.changePwdView.newPwd1.text()
        newPwd2 = self.changePwdView.newPwd2.text()
        if newPwd1 != newPwd2:
            if QMessageBox.warning(self, "提示", "两次输入的新密码不一致！         ", QMessageBox.Ok,
                                   QMessageBox.Ok) == QMessageBox.Ok:
                self.changePwdView.oldPwd.setText("")
                self.changePwdView.newPwd1.setText("")
                self.changePwdView.newPwd2.setText("")
            return
        if len(newPwd1) < 6:
            if QMessageBox.warning(self, "提示", "密码不能少于6个字符！         ", QMessageBox.Ok,
                                   QMessageBox.Ok) == QMessageBox.Ok:
                self.changePwdView.oldPwd.setText("")
                self.changePwdView.newPwd1.setText("")
                self.changePwdView.newPwd2.setText("")
            return

        if oldPwd != self.password:
            if QMessageBox.warning(self, "提示", "原始密码输入错误！         ", QMessageBox.Ok,
                                   QMessageBox.Ok) == QMessageBox.Ok:
                self.changePwdView.oldPwd.setText("")
                self.changePwdView.newPwd1.setText("")
                self.changePwdView.newPwd2.setText("")
            return
        s1 = sha1(newPwd1.encode("utf-8"))
        newPwd1_s1 = s1.hexdigest()
        sqlStr1 = "UPDATE adminuser SET upwd = '%s' WHERE uname = '%s'" % (newPwd1_s1, self.account)
        sqlStr2 = "UPDATE login SET upwd = '%s' WHERE uname = '%s'" % (newPwd1_s1, self.account)
        sqlStr3 = "UPDATE lineuser SET upwd = '%s' WHERE uname = '%s'" % (newPwd1_s1, self.account)
        try:
            self.cursor.execute(sqlStr1)
            self.db.commit()
        except Exception as e1:
            self.log_msg(flag=self.ERROR, msg_str="修改密码异常(001)", msg_tuple=e1)
            self.db.rollback()
            return
        try:
            self.cursor.execute(sqlStr2)
            self.db.commit()
        except Exception as e2:
            self.log_msg(flag=self.ERROR, msg_str="修改密码异常(002)", msg_tuple=e2)
            self.db.rollback()
            return
        try:
            self.cursor.execute(sqlStr3)
            self.db.commit()
        except Exception as e3:
            self.log_msg(flag=self.ERROR, msg_str="修改密码异常(003)", msg_tuple=e3)
            self.db.rollback()
            return
        self.password = newPwd1
        if QMessageBox.warning(self, "提示", "密码修改成功！         ", QMessageBox.Ok,
                               QMessageBox.Ok) == QMessageBox.Ok:
            self.log_msg(flag=self.INFO, msg_str="密码修改成功")
            self.changePwdView.close()

    def refreshSelf(self):
        """
        自动刷新显示列表
        :return:
        """
        ret = self.getSpoolDate(pageNo=self.curPage)
        if ret == -1:
            return
        self.updateTable()
        ret = self.getTotalPage()
        if ret == -1:
            return
        else:
            self.totalPageLable.setText("/%d(共%d页)" % (self.totalPage, self.totalPage))
            self.log_msg(flag=self.INFO, msg_str="页面自动刷新中")

    def scanner_statu_change(self):
        """
        当扫码枪未连接是，闪烁来进行提醒
        :return:
        """
        if self.scanner_statue_flag:
            self.ScanConStatu.setText("扫描枪未连接")
            self.ScanConStatu.setStyleSheet("background:red;border:none;font:bold;font-size:12px")
            self.scanner_statue_flag = False
        else:
            self.ScanConStatu.setText("扫描枪未连接")
            self.ScanConStatu.setStyleSheet("background:none;border:none;font:bold;font-size:12px")
            self.scanner_statue_flag = True

    def plc_statue_change(self):
        if self.plc_statue_flag:
            self.PlcConStatu.setText("PLC未连接")
            self.PlcConStatu.setStyleSheet("background:red;border:none;font:bold;font-size:12px")
            self.plc_statue_flag = False
        else:
            self.PlcConStatu.setText("PLC未连接")
            self.PlcConStatu.setStyleSheet("background:none;border:none;font:bold;font-size:12px")
            self.plc_statue_flag = True

    def changSetBoxColor(self, color):
        """
        修改设置栏文字颜色
        :param color:
        :return:
        """
        if self.isAdmin == True:
            self.machineID.setStyleSheet("color:%s" % color)
            self.plantID.setStyleSheet("color:%s" % color)
            self.processNo.setStyleSheet("color:%s" % color)
            self.localityNo.setStyleSheet("color:%s" % color)
            self.type.setStyleSheet("color:%s" % color)
        self.classBox.setStyleSheet("color:%s" % color)

    def setTable(self):
        """
        设置列表
        :return:
        """
        size = self.showTable.size()
        self.showTable.setColumnWidth(0, size.width() / 12)
        self.showTable.setColumnWidth(1, size.width() / 6)
        self.showTable.setColumnWidth(2, size.width() / 6)
        self.showTable.setColumnWidth(3, size.width() / 6)
        self.showTable.setColumnWidth(4, size.width() / 12)
        self.showTable.setColumnWidth(5, size.width() / 6)
        self.showTable.setColumnWidth(6, size.width() / 6)
        height = self.showTable.horizontalHeader().height()
        for i in range(0, 15):
            self.showTable.setRowHeight(i, (size.height() - height) / 15)

    def updateTable(self):
        """
        更新列表
        :return:
        """
        for i in range(0, 15):
            for j in range(0, 7):
                self.mode.setData(self.mode.index(i, j), "")
        try:
            result = self.cursor.fetchall()
            for i in range(0, len(result)):
                for j in range(0, 7):
                    if j == 0:
                        self.mode.setData(self.mode.index(i, j), str(i + 1))
                    elif j == 4:
                        if result[i][j] == 1:
                            self.mode.setData(self.mode.index(i, j), "是")
                        else:
                            self.mode.setData(self.mode.index(i, j), "否")
                    elif j == 2 or j == 5:
                        self.mode.setData(self.mode.index(i, j), str(result[i][j]))
                    else:
                        self.mode.setData(self.mode.index(i, j), result[i][j])
            self.setTable()
        except Exception as e:
            self.log_msg(flag=self.ERROR, msg_str="获取数据异常")
        gc.collect()

    def log_msg(self, flag, msg_str=None, msg_tuple=None):
        """
        打包日志信息
        :param flag:信息级别
        :param msg_str: 信息字符串
        :param msg_tuple: 信息数组
        :return:
        """
        if flag == self.DEBUG:
            if msg_str:
                self.log.debug(msg_str)
            if msg_tuple:
                self.log.debug(msg_tuple)
        elif flag == self.INFO:
            if msg_str:
                self.log.info(msg_str)
            if msg_tuple:
                self.log.info(msg_tuple)
        elif flag == self.WARNING:
            if msg_str:
                self.log.warning(msg_str)
            if msg_tuple:
                self.log.warning(msg_tuple)
        elif flag == self.ERROR:
            if msg_str:
                self.log.error(msg_str)
            if msg_tuple:
                self.log.error(msg_tuple)
        elif flag == self.CRITICAL:
            if msg_str:
                self.log.critical(msg_str)
            if msg_tuple:
                self.log.critical(msg_tuple)
        msg = {
            "code": flag,
            "msgstr": msg_str,
            "msgtuple": msg_tuple
        }
        self.msg_append(msg)

    def msg_append(self, msg):
        """
        消息加入消息队列
        :param msg:消息包
        :return:
        """
        # print(msg)
        self.mutex1.lock()
        self.msg_list.append(msg)
        self.mutex1.unlock()
        try:
            for i in self.msg_list:
                self.signal.set()
                time.sleep(0.01)
        except Exception as e:
            self.log_msg(flag=self.ERROR, msg_str="消息队列处理异常")

    def getSpoolDate(self, pageSize=15, pageNo=1):
        """
        获取工字轮数据，对应数据库gongzilun表
        :param pageSize:
        :param pageNo:
        :return:
        """
        minRow = (pageNo - 1) * pageSize
        count = pageSize
        sqlStr = "SELECT * FROM gongzilun ORDER BY id DESC LIMIT %d,%d" % (minRow, count)
        try:
            self.cursor.execute(sqlStr)
            self.db.commit()
        except Exception as e:
            self.log_msg(flag=self.ERROR, msg_tuple=e)
            return -1
        return 0

    def getTotalPage(self):
        """
        获取总页数
        :return:
        """
        sqlStr = "SELECT COUNT(*) FROM gongzilun"
        try:
            self.cursor.execute(sqlStr)
            self.db.commit()
        except Exception as e:
            self.log_msg(flag=self.ERROR, msg_tuple=e)
            return -1
        else:
            result = self.cursor.fetchall()
            self.totalPage = math.ceil(result[0][0] / 15)
            return 0

    def updateOnlineDate(self):
        """
        更新登录数据
        :return:
        """
        ret = self.clear_lineuser()
        if ret == -1:
            self.log_msg(flag=self.WARNING, msg_str="在线用户存在异常数据，未清理")
        s1 = sha1(self.password.encode("utf-8"))
        pwd = s1.hexdigest()
        sqlStr = "INSERT INTO lineuser (uname,upwd,denglushijian,runnormal)" \
                 " VALUES ('%s','%s','%s','%s')" % (self.account, pwd, self.loadTimeStr, "True")
        try:
            self.cursor.execute(sqlStr)
            self.db.commit()
        except Exception as e:
            self.log_msg(flag=self.ERROR, msg_str="更新在线账号信息异常", msg_tuple=e)
            self.db.rollback()
            return -1
        return 0

    def clear_lineuser(self):
        """
        用与清除在线用户表中的异常数据
        :return:
        """
        sqlStr = "DELETE FROM lineuser WHERE id > 0"  # WHERE uname = 'admin' OR uname = 'user'
        try:
            self.cursor.execute(sqlStr)
            self.db.commit()
        except Exception as e:
            self.log_msg(flag=self.ERROR, msg_tuple=e)
            return -1
        else:
            return 0

    def getMachineSetDate(self):
        """
        获取设置信息
        :return:
        """
        sqlStr = "SELECT * FROM machine WHERE id = 1"
        try:
            self.cursor.execute(sqlStr)
            self.db.commit()
        except Exception as e:
            self.log_msg(flag=self.ERROR, msg_tuple=e)
            return
        result = self.cursor.fetchall()
        self.machineID.setText(result[0][1])
        self.plantID.setText(result[0][2])
        self.processNo.setText(result[0][3])
        self.localityNo.setText(result[0][4])
        self.type.setText(result[0][5])
        classNo = result[0][6]
        self.classBox.setCurrentIndex(int(classNo))
        self.loadTime.setText(self.loadTimeStr)

    def updataMachineSetDate(self):
        """
        更新设置信息
        :return:
        """
        classNo = self.classBox.currentIndex()
        if self.isAdmin == True:
            machineID = self.machineID.text()
            plantID = self.plantID.text()
            processNo = self.processNo.text()
            localityNo = self.localityNo.text()
            type = self.type.text()
            sqlStr = "UPDATE machine SET shebeiid = '%s',gongchangid = '%s',gongxuid= '%s', \
                     caijidianid = '%s',caijidiantype = '%s',banci = '%s' WHERE id = 1" \
                     % (machineID, plantID, processNo, localityNo, type, str(classNo))
        if self.isAdmin == False:
            sqlStr = "UPDATE machine SET banci = '%s' WHERE id = 1" % str(classNo)
        try:
            self.cursor.execute(sqlStr)
            self.db.commit()
        except Exception as e:
            self.log_msg(flag=self.ERROR, msg_tuple=e)
            self.db.rollback()
            return -1
        return 0

    def mouseDoubleClickEvent(self, *args, **kwargs):
        """
        判断鼠标双击位置是窗口状态栏上
        :param args:
        :param kwargs:
        :return:
        """
        statu_lable_rect = self.statuLable.rect()
        statu_lable_width = statu_lable_rect.width()
        statu_lable_height = statu_lable_rect.height()
        statuLable_pos = self.statuLable.mapToGlobal(QPoint(0, 0))
        mouse_pos = args[0].globalPos()
        if statuLable_pos.x() <= mouse_pos.x() < statuLable_pos.x() + statu_lable_width and statuLable_pos.y() < mouse_pos.y() < statuLable_pos.y() + statu_lable_height:
            print("双击状态栏")

    def resizeEvent(self, *args, **kwargs):
        """
        自动调整页面
        :param args:
        :param kwargs:
        :return:
        """
        try:
            oldSize = args[0].oldSize()
            nowSize = args[0].size()
            self.statuLable.setMinimumSize(nowSize.width() / 2 - 10, 12)
            self.nowTimeLable.setMinimumSize(nowSize.width() / 2 - 10, 12)
        except Exception as e:
            self.log_msg(flag=self.ERROR, msg_tuple=e)
        if oldSize != QSize(-1, -1):
            try:
                self.layoutWidget.setGeometry(QRect(0, 10, nowSize.width() - 12, nowSize.height() - 38))
                self.setTable()
            except Exception as e2:
                self.log_msg(flag=self.ERROR, msg_str="窗口大小变动异常", msg_tuple=e2)

    def closeEvent(self, *args, **kwargs):
        """
        程序退出事件
        :param args:
        :param kwargs:
        :return:
        """
        if QMessageBox.warning(self, "提示", "确定要退出程序吗？         ", QMessageBox.Yes | QMessageBox.No,
                               QMessageBox.No) == QMessageBox.Yes:
            sqlStr = "DELETE FROM lineuser WHERE denglushijian = '%s'" % self.loadTimeStr
            try:
                self.cursor.execute(sqlStr)
                self.db.commit()
            except Exception as e:
                self.log_msg(flag=self.ERROR, msg_str="程序退出，清除用户信息异常", msg_tuple=e)
                return
            self.log_msg(flag=self.INFO, msg_str="程序退出")
            time.sleep(0.5)
            self.cursor.close()
            self.db.close()
            self.T1.isStart = False
            self.T1.quit()
            self.T1.wait()
            args[0].accept()
        else:
            args[0].ignore()

    def err_msg_work(self, msg):
        if msg["code"] == 10:  # 连接扫码枪成功
            # QMessageBox.warning(self, "提示", msg["msgstr"], QMessageBox.Yes, QMessageBox.Yes)
            self.ScanConStatu.setText("扫描枪已连接")
            self.ScanConStatu.setStyleSheet("background:#00DD00;border:none;font:bold;font-size:12px")
            self.scanner_statue_timer.stop()
        if msg["code"] == 11:  # 扫码枪未连接
            self.ScanConStatu.setText("扫描枪未连接")
            self.ScanConStatu.setStyleSheet("background:red;border:none;font:bold;font-size:12px")
            self.scanner_statue_timer.start(1000)
        if msg["code"] == 20:  # PLC连接成功
            self.PlcConStatu.setText("PLC已连接")
            self.PlcConStatu.setStyleSheet("background:#00DD00;border:none;font:bold;font-size:12px")
            self.plc_statue_timer.stop()
        if msg["code"] == 21:  # PLC未连接
            self.PlcConStatu.setText("PLC未连接")
            self.PlcConStatu.setStyleSheet("background:red;border:none;font:bold;font-size:12px")
            self.plc_statue_timer.start(1000)
        if msg["code"] == 22:  # 与PLC连接异常断开
            self.PlcConStatu.setText("PLC未连接")
            self.PlcConStatu.setStyleSheet("background:red;border:none;font:bold;font-size:12px")
            self.plc_statue_timer.start(1000)

    def run(self, *args, **kwargs):
        self.loginShow()
        self.q = args[0]
        self.q_err = args[1]
        self.T1 = get_msg_from_sys_thread(self)
        self.T2 = set_status_msg_thread(self)
        self.T3 = get_err_msg_from_sys_thread(self, self.q_err)
        self.T3.signal.connect(self.err_msg_work)
        self.T2.start()
        self.T1.isStart = True
        self.T1.start()
        # self.T3.isStart = True
        # self.T3.start()


def main(*args, **kwargs):
    app = QtWidgets.QApplication(sys.argv)
    bzj = mainView()
    bzj.run(*args, **kwargs)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
    pass
