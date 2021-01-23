# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'user_registration.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(334, 357)
        self.gridLayout_2 = QtWidgets.QGridLayout(Dialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setContentsMargins(-1, -1, -1, 12)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 10, -1, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.savePushButton = QtWidgets.QPushButton(Dialog)
        self.savePushButton.setObjectName("savePushButton")
        self.horizontalLayout.addWidget(self.savePushButton)
        self.cancelPushButton_2 = QtWidgets.QPushButton(Dialog)
        self.cancelPushButton_2.setObjectName("cancelPushButton_2")
        self.horizontalLayout.addWidget(self.cancelPushButton_2)
        self.gridLayout.addLayout(self.horizontalLayout, 8, 0, 1, 2)
        self.enterPasswordLabel = QtWidgets.QLabel(Dialog)
        self.enterPasswordLabel.setObjectName("enterPasswordLabel")
        self.gridLayout.addWidget(self.enterPasswordLabel, 4, 0, 1, 2)
        self.enterNameLabel = QtWidgets.QLabel(Dialog)
        self.enterNameLabel.setObjectName("enterNameLabel")
        self.gridLayout.addWidget(self.enterNameLabel, 0, 0, 1, 2)
        self.confirmPasswordLabel = QtWidgets.QLabel(Dialog)
        self.confirmPasswordLabel.setObjectName("confirmPasswordLabel")
        self.gridLayout.addWidget(self.confirmPasswordLabel, 6, 0, 1, 2)
        self.fullNameLineEdit = QtWidgets.QLineEdit(Dialog)
        self.fullNameLineEdit.setMinimumSize(QtCore.QSize(0, 30))
        self.fullNameLineEdit.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.fullNameLineEdit.setObjectName("fullNameLineEdit")
        self.gridLayout.addWidget(self.fullNameLineEdit, 3, 0, 1, 1)
        self.confirmLineEdit = QtWidgets.QLineEdit(Dialog)
        self.confirmLineEdit.setMinimumSize(QtCore.QSize(0, 30))
        self.confirmLineEdit.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.confirmLineEdit.setFrame(True)
        self.confirmLineEdit.setObjectName("confirmLineEdit")
        self.gridLayout.addWidget(self.confirmLineEdit, 7, 0, 1, 2)
        self.passwordLineEdit = QtWidgets.QLineEdit(Dialog)
        self.passwordLineEdit.setMinimumSize(QtCore.QSize(0, 30))
        self.passwordLineEdit.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.passwordLineEdit.setObjectName("passwordLineEdit")
        self.gridLayout.addWidget(self.passwordLineEdit, 5, 0, 1, 2)
        self.loginLineEdit = QtWidgets.QLineEdit(Dialog)
        self.loginLineEdit.setMinimumSize(QtCore.QSize(0, 30))
        self.loginLineEdit.setObjectName("loginLineEdit")
        self.gridLayout.addWidget(self.loginLineEdit, 1, 0, 1, 2)
        self.fullNameLabel = QtWidgets.QLabel(Dialog)
        self.fullNameLabel.setObjectName("fullNameLabel")
        self.gridLayout.addWidget(self.fullNameLabel, 2, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.loginLineEdit, self.passwordLineEdit)
        Dialog.setTabOrder(self.passwordLineEdit, self.confirmLineEdit)
        Dialog.setTabOrder(self.confirmLineEdit, self.savePushButton)
        Dialog.setTabOrder(self.savePushButton, self.cancelPushButton_2)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.savePushButton.setText(_translate("Dialog", "Save"))
        self.cancelPushButton_2.setText(_translate("Dialog", "Cancel"))
        self.enterPasswordLabel.setText(_translate(
            "Dialog", "<html><head/><body><p><span style=\" font-size:10pt;\">Enter password: "
                      "</span></p></body></html>"))
        self.enterNameLabel.setText(_translate(
            "Dialog", "<html><head/><body><p><span style=\" font-size:10pt;\">Enter login:"
                      "</span></p></body></html>"))
        self.confirmPasswordLabel.setText(_translate(
            "Dialog", "<html><head/><body><p><span style=\" font-size:10pt;\">Confirm password:"
                      " </span></p></body></html>"))
        self.fullNameLabel.setText(_translate(
            "Dialog", "<html><head/><body><p><span style=\" font-size:10pt;\">"
                      "Enter your full name: </span></p></body></html>"))
