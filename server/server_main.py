import socket
import sys
import logging
import argparse
import select
import time
import threading
import configparser
import os
import json
import hmac
import hashlib
import binascii
import base64
import asyncio
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSignal, QObject
from common.variables import (CONFIG_FILE_NAME, MAX_CONNECTIONS, TO, USER, ACCOUNT_NAME,
                              RESPONSE_200, RESPONSE_400, RESPONSE_511, ERROR, DATA, RESPONSE,
                              TIME, PRESENCE, FROM, EXIT, GET_CONTACTS, PUBLIC_KEY, ACTION,
                              MESSAGE_TEXT, MESSAGE, LIST_INFO, ADD_CONTACT, DELETE_CONTACT,
                              USERS_REQUEST, PUBLIC_KEY_REQUEST, RESPONSE_205, DEFAULT_PORT,
                              SEND_AVATAR, IMAGE, GET_AVATAR, RESPONSE_206,
                              GET_GROUPS, GET_MESSAGES_GROUPS, MESSAGE_GROUP)
from common.utils import get_msg, send_msg
from common.errors import IncorrectDataNotDictError
from common.decos import Logging
from common.descriptors import CheckPort, CheckIP
from database.database_server import ServerDB
from gui_server.gui_main_window import MainWindow
import logs.server_log_config
from database.mongo_db_server import MongoDbServer

LOGGER = logging.getLogger('server')
LOGGER.setLevel(logging.DEBUG)

LOCK_DATABASE = threading.Lock()


@Logging()
def get_args(default_ip, default_port):
    # Get arguments when starting the file.
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', default=default_port, type=int)
    parser.add_argument('-a', '--addr', default=default_ip)
    names = parser.parse_args(sys.argv[1:])
    address = names.addr
    port = names.port
    return address, port


def read_config_file():
    # Download server configuration file
    parser = configparser.ConfigParser()
    #  for cx-Freeze - exe file
    if getattr(sys, 'frozen', False):
        dir_path = os.path.dirname(sys.executable)
    else:
        dir_path = os.path.dirname(os.path.realpath(__file__))

    file_path = os.path.join(dir_path, f'{CONFIG_FILE_NAME}')
    parser.read(file_path, encoding='utf-8')
    if 'SETTINGS' in parser:
        return parser
    else:
        parser.add_section('SETTINGS')
        parser.set('SETTINGS', 'Default_port', str(DEFAULT_PORT))
        parser.set('SETTINGS', 'Listen_Address', '')
        parser.set('SETTINGS', 'Database_path', 'server_database.db3')

        return parser


def get_config(parser):
    port = parser['SETTINGS']['default_port']
    ip_addr = parser['SETTINGS']['listen_Address']
    db_path = parser['SETTINGS']['database_path']
    return ip_addr, port, db_path


class Server(threading.Thread, QObject):
    """Main class for connect with client"""
    # Port and Address Correction Descriptors
    listen_port = CheckPort()
    listen_ip = CheckIP()

    new_connected_client = pyqtSignal()
    disconnected_client = pyqtSignal()

    def __init__(self, listen_ip, listen_port, database, mongo_db):
        self.listen_ip = listen_ip
        self.listen_port = listen_port
        self.database = database
        self.mongo_db = mongo_db

        self.connection = None

        self.clients = []   # All clients
        self.messages = []  # All messages
        self.names = dict()  # Connected Client Names

        self.clients_read_lst = []
        self.clients_send_lst = []
        self.err_lst = []

        threading.Thread.__init__(self)
        QObject.__init__(self)

    def socket_init(self):
        # Create a socket
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Готовим сокет
        connection.bind((self.listen_ip, self.listen_port))
        connection.settimeout(0.5)
        connection.listen(MAX_CONNECTIONS)  # Слушаем порт

        self.connection = connection

    @Logging()
    def print_help(self):
        print('Supported Commands: \n'
              'users - list of known users \n'
              'connected - list of connected users \n'
              'history - user login history \n'
              'exit - server shutdown. \n'
              'help - display help for supported commands')

    @Logging()
    def get_information(self):
        time.sleep(1)
        self.print_help()
        while True:
            command = input('Enter command: ')
            if command == 'help':
                self.print_help()
            elif command == 'exit':
                break
            elif command == 'users':
                for user in sorted(self.database.users_all()):
                    print(f'User with login {user [0]}, last login: {user[2]}')
            elif command == 'connected':
                for user in sorted(self.database.users_active_list()):
                    print(f'The user with the login {user [0]} is connected ip - {user[1]} port - {user[2]}, '
                          f'connection setup time: {user[3]}')
            elif command == 'history':
                login = input(
                    'Enter user login to view history. To display the whole story, just press Enter: ')
                for user in sorted(self.database.history_login(login)):
                    print(f'User: {user [0]} login time: {user [3]}. Login from: ip - {user[1]} port - {user[2]}')
            else:
                print('Wrong command.')

    def run(self):
        # Information output on the server in a separate stream
        server_info = threading.Thread(target=self.get_information)
        server_info.daemon = True
        server_info.start()

        self.socket_init()
        # The main loop of the server program
        # We are waiting for a connection, if the timeout has expired, we catch an exception.
        while True:
            try:
                client, client_address = self.connection.accept()
            except OSError:
                pass
            else:
                LOGGER.info(f'Connection to client established - {client_address}.')
                self.clients.append(client)

            self.clients_read_lst = []
            self.clients_send_lst = []
            self.err_lst = []

            try:
                if self.clients:
                    self.clients_read_lst, self.clients_send_lst, self.err_lst = select.select\
                        (self.clients, self.clients, [], 0)
            except OSError as err:
                LOGGER.error(f'Error working with sockets: {err}')

            self.async_get_message()

            self.async_send_messages()

    @Logging()
    def async_get_message(self):
        # Get messages from clients with asyncio
        if self.clients_read_lst:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            tasks = [
                loop.create_task(self.get_messages_clients(client))
                for client in self.clients_read_lst
            ]
            wait_tasks = asyncio.wait(tasks)
            loop.run_until_complete(wait_tasks)
            loop.close()

    @Logging()
    async def get_messages_clients(self, client):
        # Receive a message from clients
            try:
                message = get_msg(client)
            except IncorrectDataNotDictError:
                LOGGER.error('Invalid data format received.')
            except (ConnectionResetError, json.decoder.JSONDecodeError, ConnectionAbortedError):
                self.remove_client(client)
            else:
                LOGGER.debug(f'Received message from client {message}.')
                await self.client_msg(message, client)

    @Logging()
    def async_send_messages(self):
        # Send messages to clients with asyncio
        if self.messages:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            tasks = [
                loop.create_task(self.send_messages(msg))
                for msg in self.messages
            ]
            wait_tasks = asyncio.wait(tasks)
            loop.run_until_complete(wait_tasks)
            loop.close()
            self.messages.clear()

    @Logging()
    async def send_messages(self, msg):
        # If there are messages to send and pending clients, send them a message.
        try:
            await self.send_message_user(msg)
        except (ConnectionResetError, ConnectionError):
            LOGGER.info(f'Communication with a client named {msg[TO]} has been lost.')
            self.clients.remove(self.names[msg[TO]])
            del self.names[msg[TO]]
            self.database.user_logout(msg[TO])
            self.disconnected_client.emit()

    @Logging()
    def checking_new_client(self, client, message):
        if message[USER][ACCOUNT_NAME] in self.names.keys():
            response = RESPONSE_400
            response[ERROR] = 'Login already taken.'
            try:
                send_msg(client, response)
            except OSError:
                pass
            self.clients.remove(client)
            client.close()
            LOGGER.debug(f'Username is already taken. Response sent to client - {response} \n')
        elif not self.database.is_user(message[USER][ACCOUNT_NAME]):
            response = RESPONSE_400
            response[ERROR] = 'User not registered.'
            try:
                send_msg(client, response)
            except OSError:
                pass
            self.clients.remove(client)
            client.close()
            LOGGER.debug(f'The user is not registered. Response sent to client - {response} \n')
        else:
            self.start_client_authorization(client, message)

    @Logging()
    def start_client_authorization(self, client, message):
        message_auth = RESPONSE_511
        random_str = binascii.hexlify(os.urandom(64))  # The hexadecimal representation of the binary data
        # Bytes cannot be in the dictionary, decode (json.dumps -> TypeError)
        message_auth[DATA] = random_str.decode('ascii')
        password_hash = self.database.get_hash(message[USER][ACCOUNT_NAME])
        hash = hmac.new(password_hash, random_str)
        server_digest = hash.digest()

        try:
            send_msg(client, message_auth)
            answer = get_msg(client)
        except OSError:
            client.close()
            return

        client_digest = binascii.a2b_base64(answer[DATA])

        if RESPONSE in answer and answer[RESPONSE] == 511 and hmac.compare_digest(server_digest, client_digest):
            self.names[message[USER][ACCOUNT_NAME]] = client
            client_ip, client_port = client.getpeername()
            try:
                send_msg(client, RESPONSE_200)
            except OSError:
                self.remove_client(message[USER][ACCOUNT_NAME])

            self.database.login_user(message[USER][ACCOUNT_NAME],
                                     client_ip, client_port, message[USER][PUBLIC_KEY])
            LOGGER.info(F'Successful user authentication {message[USER][ACCOUNT_NAME]}')
            self.new_connected_client.emit()
        else:
            response = RESPONSE_400
            response[ERROR] = 'Wrong password.'
            try:
                send_msg(client, response)
            except OSError:
                pass
            self.clients.remove(client)
            client.close()

    @Logging()
    def is_added_new_user(self, password, login_user, fullname):
        try:
            password_bytes = password.encode('utf-8')
            salt = login_user.encode('utf-8')
            password_hash = hashlib.pbkdf2_hmac('sha512', password_bytes, salt, 10000)
            password_hash_str = binascii.hexlify(password_hash)
        except ValueError:
            return False
        else:
            with LOCK_DATABASE:
                self.database.add_user(login_user, password_hash_str, fullname)
                self.mongo_db.add_user(login_user, password_hash_str, fullname)
            self.update_users_list_message()
            return True

    @Logging()
    def remove_client(self, client):
        LOGGER.info(f'Client {client.getpeername ()} disconnected from server.')
        for name in self.names:
            if self.names[name] == client:
                self.database.user_logout(name)
                del self.names[name]
                break
        self.clients.remove(client)
        client.close()
        self.disconnected_client.emit()

    @Logging()
    async def client_msg(self, message, client):
        LOGGER.debug(f'Parsing a message from a client - {message}')
        if ACTION in message and TIME in message and USER in message \
                and ACCOUNT_NAME in message[USER] \
                and message[ACTION] == PRESENCE\
                and PUBLIC_KEY in message[USER]:
            self.checking_new_client(client, message)

        elif ACTION in message and message[ACTION] == MESSAGE and\
                TIME in message and MESSAGE_TEXT in message and TO in message and FROM in message:
            if message[TO] in self.names:
                self.messages.append(message)
                send_msg(client, {RESPONSE: 200})
            else:
                send_msg(client, {RESPONSE: 400, ERROR: 'The user is not registered on the server.'})

        elif ACTION in message and message[ACTION] == MESSAGE_GROUP and\
                TIME in message and MESSAGE_TEXT in message and TO in message and FROM in message:
            with LOCK_DATABASE:
                self.database.add_group_message(message[TO], message[FROM], message[MESSAGE_TEXT])
            send_msg(client, {RESPONSE: 200})
            self.send_group_message(message)

        elif ACTION in message and message[ACTION] == GET_CONTACTS and USER in message \
                and self.names[message[USER]] == client:
            answer = {
                RESPONSE: 202,
                LIST_INFO: self.database.get_contacts(message[USER])
                }
            send_msg(client, answer)
            LOGGER.debug(f'Contact list sent to {answer [LIST_INFO]} to user - {message[USER]}\n')

        elif ACTION in message and message[ACTION] == GET_GROUPS and USER in message \
                and self.names[message[USER]] == client:
            answer = {
                RESPONSE: 202,
                LIST_INFO: [group[1] for group in self.database.get_groups()]
                }
            send_msg(client, answer)
            LOGGER.debug(f'Groups list sent to {answer [LIST_INFO]} to user - {message[USER]}\n')

        elif ACTION in message and message[ACTION] == GET_MESSAGES_GROUPS and USER in message \
                and self.names[message[USER]] == client:
            answer = {
                RESPONSE: 202,
                LIST_INFO: self.database.get_messages_groups()
                }
            send_msg(client, answer)
            LOGGER.debug(f'Groups list sent to {answer [LIST_INFO]} to user - {message[USER]}\n')

        elif ACTION in message and message[ACTION] == ADD_CONTACT \
                and ACCOUNT_NAME in message and USER in message \
                and self.names[message[USER]] == client:
            self.database.add_contact(message[USER], message[ACCOUNT_NAME])
            send_msg(client, {RESPONSE: 200})
            LOGGER.debug(f'New contact added {message[ACCOUNT_NAME]} ay the user {message[USER]}.')

        elif ACTION in message and message[ACTION] == DELETE_CONTACT and ACCOUNT_NAME in message and USER in message \
                and self.names[message[USER]] == client:
            self.database.delete_contact(message[USER], message[ACCOUNT_NAME])
            send_msg(client, RESPONSE_200)
            LOGGER.debug(f'Deleted contact {message [ACCOUNT_NAME]} at the user {message [USER]}')

        elif ACTION in message and message[ACTION] == USERS_REQUEST and ACCOUNT_NAME in message \
                and self.names[message[ACCOUNT_NAME]] == client:
            answer = {
                RESPONSE: 202,
                LIST_INFO: [user[0] for user in self.database.users_all()]
            }
            send_msg(client, answer)

        elif ACTION in message and message[ACTION] == PUBLIC_KEY_REQUEST and ACCOUNT_NAME in message:
            response = RESPONSE_511
            response[DATA] = self.database.get_pubkey(message[ACCOUNT_NAME])
            if response[DATA]:
                try:
                    send_msg(client, response)
                except OSError:
                    self.remove_client(client)
            else:
                response = RESPONSE_400
                response[ERROR] = 'There is no public key for this user.'
                try:
                    send_msg(client, response)
                except OSError:
                    self.remove_client(client)

        elif ACTION in message and message[ACTION] == SEND_AVATAR \
                and USER in message and ACCOUNT_NAME in message[USER]\
                and IMAGE in message[USER]:
            try:
                send_msg(client, RESPONSE_200)
            except OSError:
                self.remove_client(client)
            else:
                img = message[USER][IMAGE]
                login = message[USER][ACCOUNT_NAME]
                img_data = base64.b64decode(img)
                filename = f'img/avatar_{login}.jpg'
                with open(filename, 'wb') as f:
                    f.write(img_data)

                self.database.add_image_path(login, filename)
                LOGGER.debug(f'Added avatar for {client}')

        elif ACTION in message and message[ACTION] == GET_AVATAR \
                and ACCOUNT_NAME in message:
            login = message[ACCOUNT_NAME]
            filename = f'img/avatar_{login}.jpg'
            try:
                with open(filename, 'rb') as image_file:
                    encoded_img = base64.b64encode(image_file.read()).decode('utf8')
            except FileNotFoundError:
                response = RESPONSE_400
                response[ERROR] = f'Not found avatar {login}'
            else:
                response = RESPONSE_511
                response[DATA] = encoded_img
            try:
                send_msg(client, response)
            except OSError:
                self.remove_client(client)

        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
            LOGGER.info(f'User {message [ACCOUNT_NAME]} has disconnected.')
            user_name = message[ACCOUNT_NAME]
            self.database.user_logout(user_name)
            self.clients.remove(self.names[user_name])
            self.names[user_name].close()
            del self.names[user_name]
            self.disconnected_client.emit()

        else:
            msg = {
                RESPONSE: 400,
                ERROR: 'Bad Request'
            }
            send_msg(client, msg)
            LOGGER.info(f'Errors sent to client - {msg}.\n')

    @Logging()
    async def send_message_user(self, msg):
        """Function respond to users."""
        if msg[TO] in self.names and self.names[msg[TO]] in self.clients_send_lst:
            send_msg(self.names[msg[TO]], msg)
            self.database.sending_message(msg[FROM], msg[TO])
            LOGGER.info(f'A message was sent to user {msg [TO]} from user {msg [FROM]}.')
        elif msg[TO] in self.names and self.names[msg[TO]] not in self.clients_send_lst:
            raise ConnectionError
        else:
            LOGGER.error(
                f'User {msg [TO]} is not registered on the server, sending messages is not possible.')

    def update_users_list_message(self):
        """A method that implements sending a service message to 205 clients."""
        for client in self.names:
            try:
                msg = RESPONSE_205
                msg[LIST_INFO] = [user[0] for user in self.database.users_all()]
                send_msg(self.names[client], msg)
            except OSError:
                self.remove_client(self.names[client])

    @Logging()
    def is_remove_user(self, login):
        with LOCK_DATABASE:
            self.database.remove_user(login)
        self.update_users_list_message()
        return True

    @Logging()
    def send_groups(self):
        for client in self.names:
            try:
                msg = RESPONSE_206
                msg[LIST_INFO] = [group[1] for group in self.database.get_groups()]
                send_msg(self.names[client], msg)
            except OSError:
                self.remove_client(self.names[client])

    @Logging()
    def create_new_group(self, group_name):
        self.database.add_new_group(group_name)
        self.send_groups()

    @Logging()
    def send_group_message(self, message):
        for client in self.names:
            if client != message[FROM]:
                try:
                    send_msg(self.names[client], message)
                except OSError:
                    self.remove_client(self.names[client])

    @Logging()
    def close_socket(self):
        self.connection.close()


@Logging()
def main():
    parser = read_config_file()
    default_ip, default_port, db_path = get_config(parser)
    listen_ip, listen_port = get_args(default_ip, default_port)

    database = ServerDB(db_path)

    # Create Mongo database
    mongo_db = MongoDbServer()

    server = Server(listen_ip, listen_port, database, mongo_db)
    server.daemon = True
    server.start()

    # GUI PyQt5
    app = QApplication(sys.argv)
    main_window = MainWindow(app, database, server, parser)
    main_window.init_ui()
    main_window.make_connection_signals(server)
    app.exec_()

    server.close_socket()


if __name__ == '__main__':
    main()
