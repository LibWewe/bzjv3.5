# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'loginWin.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(332, 175)
        self.loginBtn = QtWidgets.QPushButton(Form)
        self.loginBtn.setGeometry(QtCore.QRect(70, 120, 201, 23))
        self.loginBtn.setObjectName("loginBtn")
        self.account = QtWidgets.QLineEdit(Form)
        self.account.setGeometry(QtCore.QRect(70, 30, 201, 20))
        self.account.setObjectName("account")
        self.password = QtWidgets.QLineEdit(Form)
        self.password.setGeometry(QtCore.QRect(70, 70, 201, 20))
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password.setObjectName("password")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)
        Form.setTabOrder(self.account, self.password)
        Form.setTabOrder(self.password, self.loginBtn)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "登陆"))
        self.loginBtn.setText(_translate("Form", "登陆"))

