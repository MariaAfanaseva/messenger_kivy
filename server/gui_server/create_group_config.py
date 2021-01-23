# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'create_group.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(334, 165)
        self.gridLayout_2 = QtWidgets.QGridLayout(Dialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setContentsMargins(-1, -1, -1, 12)
        self.gridLayout.setObjectName("gridLayout")
        self.nameLineEdit = QtWidgets.QLineEdit(Dialog)
        self.nameLineEdit.setMinimumSize(QtCore.QSize(0, 30))
        self.nameLineEdit.setObjectName("nameLineEdit")
        self.gridLayout.addWidget(self.nameLineEdit, 1, 0, 1, 2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 10, -1, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.savePushButton = QtWidgets.QPushButton(Dialog)
        self.savePushButton.setObjectName("savePushButton")
        self.horizontalLayout.addWidget(self.savePushButton)
        self.cancelPushButton = QtWidgets.QPushButton(Dialog)
        self.cancelPushButton.setObjectName("cancelPushButton")
        self.horizontalLayout.addWidget(self.cancelPushButton)
        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 1, 2)
        self.enterNameLabel = QtWidgets.QLabel(Dialog)
        self.enterNameLabel.setObjectName("enterNameLabel")
        self.gridLayout.addWidget(self.enterNameLabel, 0, 0, 1, 2)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.nameLineEdit, self.savePushButton)
        Dialog.setTabOrder(self.savePushButton, self.cancelPushButton)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.savePushButton.setText(_translate("Dialog", "Save"))
        self.cancelPushButton.setText(_translate("Dialog", "Cancel"))
        self.enterNameLabel.setText(_translate("Dialog", "<html><head/><body><p><span style=\" font-size:10pt;\">Enter name for group:</span></p></body></html>"))
