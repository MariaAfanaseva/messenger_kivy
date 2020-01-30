import sys
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from gui_server.remove_user_convig import Ui_Dialog


class DelUserConfirmation(QDialog):
    """Create new window for remove user."""
    def __init__(self, server_transport, del_user_login):
        self.server_transport = server_transport
        self.del_user_login = del_user_login
        self.message_window = QMessageBox()
        super().__init__()

    def init_ui(self):
        self.user_interface = Ui_Dialog()
        self.user_interface.setupUi(self)
        self.user_interface.cancelButton.clicked.connect(self.close)
        self.user_interface.removeButton.clicked.connect(self.remove_user)
        self.user_interface.label.setText(
            f'Are you sure you want to remove user {self.del_user_login}?')
        self.user_interface.label.setAlignment(Qt.AlignCenter)
        self.user_interface.label.setFont(QtGui.QFont('SansSerif', 10))
        self.show()

    def remove_user(self):
        if self.server_transport.is_remove_user(self.del_user_login):
            self.message_window.information(self, 'Success', 'User successfully removed.')
            self.close()
        else:
            self.message_window.information(self, 'Error', 'Failed to delete user')
            self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = DelUserConfirmation('test1')
    main_window.init_ui()
    sys.exit(app.exec_())
