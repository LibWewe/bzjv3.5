# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'logMsgWin.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(500, 580)
        Form.setMinimumSize(QtCore.QSize(500, 580))
        Form.setMaximumSize(QtCore.QSize(500, 580))
        self.log_msg_edit = QtWidgets.QTextEdit(Form)
        self.log_msg_edit.setGeometry(QtCore.QRect(0, 0, 551, 481))
        self.log_msg_edit.setObjectName("log_msg_edit")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))

