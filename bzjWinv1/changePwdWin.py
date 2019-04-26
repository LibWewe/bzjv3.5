# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'changePwdWin.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(351, 272)
        self.layoutWidget = QtWidgets.QWidget(Form)
        self.layoutWidget.setGeometry(QtCore.QRect(60, 20, 241, 201))
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.oldPwd = QtWidgets.QLineEdit(self.layoutWidget)
        self.oldPwd.setEchoMode(QtWidgets.QLineEdit.Password)
        self.oldPwd.setObjectName("oldPwd")
        self.gridLayout.addWidget(self.oldPwd, 0, 0, 1, 1)
        self.newPwd1 = QtWidgets.QLineEdit(self.layoutWidget)
        self.newPwd1.setEchoMode(QtWidgets.QLineEdit.Password)
        self.newPwd1.setObjectName("newPwd1")
        self.gridLayout.addWidget(self.newPwd1, 1, 0, 1, 1)
        self.newPwd2 = QtWidgets.QLineEdit(self.layoutWidget)
        self.newPwd2.setEchoMode(QtWidgets.QLineEdit.Password)
        self.newPwd2.setObjectName("newPwd2")
        self.gridLayout.addWidget(self.newPwd2, 2, 0, 1, 1)
        self.changeBtn = QtWidgets.QPushButton(self.layoutWidget)
        self.changeBtn.setObjectName("changeBtn")
        self.gridLayout.addWidget(self.changeBtn, 3, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "修改密码"))
        self.changeBtn.setText(_translate("Form", "确认修改"))

