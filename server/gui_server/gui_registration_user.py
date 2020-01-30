import sys
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox
from gui_server.user_registration_config import Ui_Dialog


class RegistrationDialog(QDialog):
    """
    Window for registration user.
    Required fields - login, password, confirm password.
    Save hash password.
    """

    def __init__(self, database, server):
        self.database = database
        self.server = server
        self.message_window = QMessageBox
        super().__init__()

    def init_ui(self):
        self.user_interface = Ui_Dialog()
        self.user_interface.setupUi(self)
        self.user_interface.cancelPushButton_2.clicked.connect(self.close)
        self.user_interface.savePushButton.clicked.connect(self.registration_user)
        self.show()

    def registration_user(self):
        login_user = self.user_interface.loginLineEdit.text()
        password = self.user_interface.passwordLineEdit.text()
        confirm_password = self.user_interface.confirmLineEdit.text()
        fullname = self.user_interface.fullNameLineEdit.text()

        if login_user and password and confirm_password:
            if password != confirm_password:
                self.message_window.critical(self, 'Error', 'The entered passwords do not match.')
                return
            elif self.database.is_user(login_user):
                self.message_window.critical(self, 'Error', 'User already exists.')
                return
            else:
                if self.server.is_added_new_user(password, login_user, fullname):
                    self.message_window.information(self, 'Success', 'User successfully registered.')
                    self.close()
        else:
            self.message_window.information(self, 'Warning', 'Required fields all, but full name.')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = RegistrationDialog(app)
    main_window.init_ui()
    sys.exit(app.exec_())
