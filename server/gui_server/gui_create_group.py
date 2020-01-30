import sys
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox
from gui_server.create_group_config import Ui_Dialog


class CreateGroupDialog(QDialog):
    """
    Window for create new group.
    """
    def __init__(self, server):
        self.server = server
        self.message_window = QMessageBox
        super().__init__()

    def init_ui(self):
        self.user_interface = Ui_Dialog()
        self.user_interface.setupUi(self)
        self.user_interface.cancelPushButton.clicked.connect(self.close)
        self.user_interface.savePushButton.clicked.connect(self.create_group)
        self.show()

    def create_group(self):
        group_name = self.user_interface.nameLineEdit.text()
        if group_name:
            self.server.create_new_group(group_name)
            self.close()
