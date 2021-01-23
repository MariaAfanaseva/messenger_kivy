import configparser
import os
from ipaddress import ip_address
from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QDialog, QPushButton, QFileDialog, QLineEdit, QMessageBox
from common.variables import CONFIG_FILE_NAME


class SettingsWindow(QDialog):
    """Window settings. Save settings in file .ini"""
    def __init__(self, parser):
        self.parser = parser
        super().__init__()

    def init_ui(self):
        self.setFixedSize(500, 350)
        self.move(600, 400)

        self.setWindowTitle('Settings server')

        self.central_widget = QWidget(self)
        self.layout = QGridLayout(self.central_widget)
        self.db_path_label = QLabel('Path database: ', self)
        self.db_path_label.setFont(QtGui.QFont('Montserrat', 10))
        self.db_path_select = QPushButton('Select...', self)

        self.db_path_text = QLineEdit(self)
        self.db_path_text.setReadOnly(True)
        self.db_path_text.setFixedSize(300, 28)
        self.db_path_text.setFont(QtGui.QFont('Montserrat', 10))

        self.port_label = QLabel('Port number:', self)
        self.port_label.setFont(QtGui.QFont('Montserrat', 10))

        # Port number input field
        self.port = QLineEdit(self)
        self.port.setFixedSize(80, 28)
        self.port.setFont(QtGui.QFont('Montserrat', 10))

        self.ip_label = QLabel('IP address:', self)
        self.ip_label.setFont(QtGui.QFont('Montserrat', 10))

        self.ip = QLineEdit(self)
        self.ip.setFixedSize(120, 28)
        self.ip.setFont(QtGui.QFont('Montserrat', 10))

        self.ip_label_note = QLabel('Leave this field blank\n'
                                    'to accept connections from any addresses.', self)
        self.ip_label_note.setFixedSize(350, 50)
        self.ip_label_note.setFont(QtGui.QFont('Montserrat', 8))

        self.save_button = QPushButton('Save', self)
        self.save_button.setFixedSize(100, 30)
        self.save_button.clicked.connect(self.save_server_config)

        self.close_button = QPushButton('Close', self)
        self.close_button.setFixedSize(100, 30)
        self.close_button.clicked.connect(self.close)

        self.layout.addWidget(self.db_path_label, 0, 0)
        self.layout.addWidget(self.db_path_text, 1, 0)
        self.layout.addWidget(self.db_path_select, 1, 1)
        self.layout.addWidget(self.port_label, 2, 0)
        self.layout.addWidget(self.port, 3, 0)
        self.layout.addWidget(self.ip_label, 4, 0)
        self.layout.addWidget(self.ip, 5, 0)
        self.layout.addWidget(self.ip_label_note, 6, 0)
        self.layout.addWidget(self.save_button, 7, 0, 2, 1)
        self.layout.addWidget(self.close_button, 7, 1)

        self.layout.setContentsMargins(20, 30, 0, 0)
        self.db_path_select.clicked.connect(self.open_file_select)

        self.config_file_text_print()

        self.show()

    def open_file_select(self):
        dialog = QFileDialog(self)
        path = dialog.getOpenFileName()
        path = path[0]
        self.db_path_text.clear()
        self.db_path_text.insert(path)

    def config_file_text_print(self):
        db_path_config = self.parser['SETTINGS']['database_path']
        config_port = self.parser['SETTINGS']['default_port']
        config_addr = self.parser['SETTINGS']['listen_Address']

        self.db_path_text.insert(db_path_config)
        self.port.insert(config_port)
        self.ip.insert(config_addr)

    def save_server_config(self):
        message = QMessageBox()
        self.parser['SETTINGS']['database_path'] = self.db_path_text.text()

        try:
            port = int(self.port.text())
            ip_addr = self.ip.text()
            if ip_addr:
                try:
                    str(ip_address(ip_addr))
                except ValueError:
                    message.warning(self, 'Error', 'Invalid ip format.')
        except ValueError:
            message.warning(self, 'Error', 'The port must be a number')
        else:
            self.parser['SETTINGS']['listen_Address'] = ip_addr
            if 1024 < port < 65535:
                self.parser['SETTINGS']['default_port'] = str(port)

                dir_path = os.path.dirname(os.path.abspath(__file__))
                self.file_path = os.path.join(dir_path, '../', CONFIG_FILE_NAME)

                with open(self.file_path, 'w', encoding='utf-8') as file:
                    self.parser.write(file)
                    message.information(self, 'OK', 'Settings saved successfully!')
                    self.close()
            else:
                message.warning(self, 'Ошибка', 'The port must be between 1024 and 65536')
