# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'del_user_window_main.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(590, 627)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        self.gridLayout_2 = QtWidgets.QGridLayout(Dialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.updateAllUsersList = QtWidgets.QPushButton(Dialog)
        self.updateAllUsersList.setObjectName("updateAllUsersList")
        self.gridLayout.addWidget(self.updateAllUsersList, 0, 1, 1, 1)
        self.allUsersLabel = QtWidgets.QLabel(Dialog)
        self.allUsersLabel.setObjectName("allUsersLabel")
        self.gridLayout.addWidget(self.allUsersLabel, 0, 0, 1, 1)
        self.cancelWindow = QtWidgets.QPushButton(Dialog)
        self.cancelWindow.setObjectName("cancelWindow")
        self.gridLayout.addWidget(self.cancelWindow, 4, 1, 1, 1)
        self.delUserButton = QtWidgets.QPushButton(Dialog)
        self.delUserButton.setObjectName("delUserButton")
        self.gridLayout.addWidget(self.delUserButton, 4, 0, 1, 1)
        self.usersAllTableView = QtWidgets.QTableView(Dialog)
        self.usersAllTableView.setObjectName("usersAllTableView")
        self.gridLayout.addWidget(self.usersAllTableView, 1, 0, 1, 2)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.updateAllUsersList.setText(_translate("Dialog", "Update users all list"))
        self.allUsersLabel.setText(_translate("Dialog", "<html><head/><body><p><span style=\" font-size:10pt;\">All users list</span></p></body></html>"))
        self.cancelWindow.setText(_translate("Dialog", "Cancel"))
        self.delUserButton.setText(_translate("Dialog", "Remove user"))
