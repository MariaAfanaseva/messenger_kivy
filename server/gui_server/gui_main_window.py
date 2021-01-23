import sys
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QApplication, QTableView, QMainWindow, \
    QAction, QLabel, QGridLayout, QMenu
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from gui_server.gui_settings_window import SettingsWindow
from gui_server.gui_registration_user import RegistrationDialog
from gui_server.gui_remove_user import RemoveUserDialog
from gui_server.gui_create_group import CreateGroupDialog


class MainWindow(QMainWindow):
    """Class main window for user. Contains contacts list, text edit and history messages"""
    def __init__(self, app, database, server, parser):
        self.app = app
        self.database = database
        self.server = server
        self.parser = parser
        super().__init__()

    def init_ui(self):
        self.resize(700, 600)
        self.move(500, 300)

        self.setWindowTitle('Server')

        self.statusBar()

        exit_action = QAction('Close', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.app.quit)

        update_connected_users_action = QAction('Update connected users', self)
        update_connected_users_action.triggered.connect(self.update_connected_users_list)

        server_settings_action = QAction('Settings', self)
        server_settings_action.triggered.connect(self.settings_window_open)

        add_user = QAction('Registration user', self)
        add_user.triggered.connect(self.registration_dialog_open)

        rm_user = QAction('Remove user', self)
        rm_user.triggered.connect(self.user_remove)

        menu_users = QMenu('Users', self)
        menu_users.setObjectName("menu_users")
        menu_users.addAction(add_user)
        menu_users.addAction(rm_user)

        create_group = QAction('Create group', self)
        create_group.triggered.connect(self.create_group)

        menu_groups = QMenu('Groups', self)
        menu_groups.setObjectName("menu_groups")
        menu_groups.addAction(create_group)

        self.toolbar = self.addToolBar('MainBar')
        self.toolbar.setFont(QtGui.QFont('Montserrat', 10))
        self.toolbar.addAction(update_connected_users_action)
        self.toolbar.addAction(menu_users.menuAction())
        self.toolbar.addAction(menu_groups.menuAction())
        self.toolbar.addAction(server_settings_action)
        self.toolbar.addAction(exit_action)

        self.central_widget = QWidget(self)
        self.layout = QGridLayout(self.central_widget)

        self.connected_users_label = QLabel('Connected users:')
        self.connected_users_label.setFont(QtGui.QFont('Montserrat', 10))
        self.connected_users_table = QTableView(self)

        self.connected_users_table.setFont(QtGui.QFont('Montserrat', 10))

        self.connected_users_list = QStandardItemModel(self)
        self.connected_users_table.setModel(self.connected_users_list)

        self.layout.addWidget(self.connected_users_label, 0, 0)
        self.layout.addWidget(self.connected_users_table, 1, 0)

        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        self.statusBar().showMessage("Server Working")

        self.update_connected_users_list()

        self.show()

    def registration_dialog_open(self):
        self.registration = RegistrationDialog(self.database, self.server)
        self.registration.init_ui()

    def user_remove(self):
        self.del_user_window = RemoveUserDialog(self.database, self.server)
        self.del_user_window.init_ui()
        
    def settings_window_open(self):
        self.settings_window = SettingsWindow(self.parser)
        self.settings_window.init_ui()

    def add_connected_user(self, user_name, ip_address, port, connection_time):
        user_name = QStandardItem(user_name)
        user_name.setEditable(False)  # forbidden to enter text
        ip_address = QStandardItem(ip_address)
        ip_address.setEditable(False)
        port = QStandardItem(port)
        port.setEditable(False)
        connection_time = QStandardItem(connection_time)
        connection_time.setEditable(False)
        self.connected_users_list.appendRow([user_name, ip_address, port, connection_time])

    def update_connected_users_list(self):
        users = self.database.users_active_list()
        self.connected_users_list.clear()
        self.connected_users_list.setHorizontalHeaderLabels(['Name', 'IP', 'Port', 'Connection time'])

        for name, ip, port, time in users:
            self.add_connected_user(name, ip, str(port), time.strftime("%m/%d/%Y, %H:%M:%S"))

        #  Align Date Column
        self.connected_users_table.resizeColumnToContents(3)

    def create_group(self):
        self.create_group_window = CreateGroupDialog(self.server)
        self.create_group_window.init_ui()

    @pyqtSlot()
    def update_connected_users_slot(self):
        """Slot update connected users list on main window"""
        self.update_connected_users_list()

    def make_connection_signals(self, transport_server_obj):
        """Signal connection method."""
        transport_server_obj.new_connected_client.connect(self.update_connected_users_slot)
        transport_server_obj.disconnected_client.connect(self.update_connected_users_slot)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow(app)
    main_window.init_ui()
    # main_window.update_connected_users_list()
    sys.exit(app.exec_())
