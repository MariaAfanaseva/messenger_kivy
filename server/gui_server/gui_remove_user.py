import sys
from PyQt5 import QtGui
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from gui_server.del_user_window_main_config import Ui_Dialog
from database.database_server import ServerDB
from gui_server.gui_remove_confirmation import DelUserConfirmation


class RemoveUserDialog(QDialog):
    """Create window for remove user."""
    def __init__(self, database_server, server_transport):
        self.database_server = database_server
        self.server_transport = server_transport
        self.message_window = QMessageBox()
        super().__init__()

    def init_ui(self):
        self.user_interface = Ui_Dialog()
        self.user_interface.setupUi(self)

        self.user_interface.cancelWindow.clicked.connect(self.close)
        self.user_interface.updateAllUsersList.clicked.connect(self.update_users_all)
        self.user_interface.delUserButton.clicked.connect(self.del_user)
        self.user_interface.usersAllTableView.setFont(QtGui.QFont('Montserrat', 10))
        self.users_all_model = QStandardItemModel(self)
        self.user_interface.usersAllTableView.setModel(self.users_all_model)
        self.update_users_all()
        self.show()

    def del_user(self):
        """Method for calling the delete user window."""
        self.del_user_login = self.user_interface.usersAllTableView.currentIndex().data()
        print(self.user_interface.usersAllTableView.currentIndex())
        print(self.del_user_login)
        if not self.del_user_login:
            self.message_window.information(self, 'Warning', 'Select a user name to delete!')
        else:
            self.del_user_window = DelUserConfirmation(self.server_transport, self.del_user_login)
            self.del_user_window.init_ui()
            self.del_user_window.user_interface.removeButton.clicked.connect(self.update_users_all)

    def update_users_all(self):
        users_all = self.database_server.users_all()
        self.users_all_model.clear()
        self.users_all_model.setHorizontalHeaderLabels(['Login', 'Fullname', 'Last login'])

        for login, fullname, last_login in users_all:
            login = QStandardItem(login)
            login.setEditable(False)  # forbidden to enter text
            fullname = QStandardItem(fullname)
            fullname.setEditable(False)
            fullname.setEnabled(False)
            last_login = QStandardItem(last_login.strftime("%m/%d/%Y, %H:%M:%S"))
            last_login.setEditable(False)
            last_login.setEnabled(False)
            self.users_all_model.appendRow([login, fullname, last_login])

        #  Align Date Column
        self.user_interface.usersAllTableView.resizeColumnToContents(2)


if __name__ == '__main__':
    database = ServerDB('server_database.py')
    app = QApplication(sys.argv)
    main_window = RemoveUserDialog(database)
    main_window.init_ui()
    sys.exit(app.exec_())
