import sys
import time
import socket
import logging
import argparse
import threading
import hashlib
import hmac
import binascii
import json
import base64
from database.mongo_db_client import MongoDbClient
from PyQt5.QtCore import pyqtSignal, QObject
from common.utils import get_msg, send_msg
from common.variables import (DEFAULT_IP_ADDRESS, DEFAULT_PORT, TO, USER, ACCOUNT_NAME,
                              RESPONSE_511, ERROR, DATA, RESPONSE, TIME, PRESENCE, FROM,
                              EXIT, GET_CONTACTS, PUBLIC_KEY, ACTION, MESSAGE_TEXT, MESSAGE,
                              LIST_INFO, ADD_CONTACT, DELETE_CONTACT, USERS_REQUEST,
                              PUBLIC_KEY_REQUEST, SEND_AVATAR, IMAGE, GET_AVATAR,
                              GET_GROUPS, get_path_avatar, GET_MESSAGES_GROUPS, MESSAGE_GROUP)
from common.errors import (IncorrectDataNotDictError, FieldMissingError,
                           IncorrectCodeError, ServerError)
from common.decos import Logging
from common.descriptors import CheckPort, CheckIP, CheckName
from database.database_client import ClientDB
from encrypt_decrypt import EncryptDecrypt
import logs.client_log_config
from gui_kivy.signal import KivySignal


LOGGER = logging.getLogger('client')

LOCK_DATABASE = threading.Lock()
LOCK_SOCKET = threading.Lock()


@Logging()
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-ip', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('-port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    parser.add_argument('-p', '--password', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_ip = namespace.ip
    server_port = namespace.port
    login_client = namespace.name
    password_client = namespace.password
    return server_ip, server_port


class Client(threading.Thread, QObject):
    """Performs initial client connection to the server, updating the database"""
    server_port = CheckPort()
    server_ip = CheckIP()
    client_login = CheckName()

    # Load window signals
    connection_lack_signal = KivySignal()
    progressbar_signal = KivySignal()
    answer_server = KivySignal()

    #  Main window signals
    new_message_signal_chat = KivySignal()
    new_message_signal_contacts = KivySignal()
    new_message_group_signal = pyqtSignal(str)
    connection_lost_signal = pyqtSignal()
    new_group_signal = pyqtSignal()

    def __init__(self, connection, server_ip, server_port, client_login,
                 client_password, database, mongo_db, encrypt_decrypt):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_login = client_login
        self.client_password = client_password
        self.database = database
        self.mongo_db = mongo_db
        self.connection = connection
        self.encrypt_decrypt = encrypt_decrypt
        self.pubkey = encrypt_decrypt.get_pubkey_user()

        self.is_connected = False

        threading.Thread.__init__(self)
        QObject.__init__(self)

    @Logging()
    def run(self):
        print(f'Console messenger. Client module. Welcome: {self.client_login}')
        LOGGER.info(
            f'Launched client with parameters: server address: {self.server_ip} ,'
            f' port: {self.server_port}, username: {self.client_login}')
        # Timeout 1 second needed to free socket
        self.connection.settimeout(1)

        for i in range(5):
            LOGGER.info(f'Connection attempt - {i + 1}.')
            print(f'Connection attempt - {i + 1}.')
            try:
                self.connection.connect((self.server_ip, self.server_port))
            except (OSError, ConnectionRefusedError):
                pass
            else:
                self.is_connected = True
                break
            time.sleep(1)

        if not self.is_connected:
            LOGGER.critical('Unable to establish a connection. '
                            'Invalid ip or port or server is down.\n')
            self.connection_lack()

        LOGGER.debug(f'Server connection established.')

        self.start_authorization_procedure()

        self.load_database()

        self.get_message_from_server()

    @Logging()
    def start_authorization_procedure(self):
        pubkey = self.pubkey.decode('ascii')
        msg_to_server = self.create_presence_msg(self.client_login, pubkey)

        LOGGER.info(f'A message has been generated to the server - {msg_to_server}.')
        try:
            send_msg(self.connection, msg_to_server)
            LOGGER.debug(f'Message sent to server.')

            answer_all = get_msg(self.connection)
            answer_code = self.answer_server_presence(answer_all)
            LOGGER.info(f'Received response from server - {answer_code}.\n')

            self.send_hash_password(answer_all)

            answer_code = self.answer_server_presence(get_msg(self.connection))

        except json.JSONDecodeError:
            LOGGER.error('Failed to decode received Json string.')
            self.connection_lack()
        except IncorrectDataNotDictError:
            LOGGER.error('Invalid data format received.\n')
            self.connection_lack()
        except FieldMissingError as missing_error:
            LOGGER.error(f'No required field - {missing_error}.\n')
            self.connection_lack()
        except IncorrectCodeError as wrong_code:
            LOGGER.error(f'Invalid code in message - {wrong_code}.')
            self.connection_lack()
        except ConnectionResetError:
            LOGGER.critical('Server connection not established.')
            self.connection_lack()
        except ServerError as er:
            LOGGER.critical(f'{er}')
            self.is_connected = False
            self.answer_server.emit(f'{er}', 'login')
            exit(1)
        else:
            LOGGER.info(f'Received response from server - {answer_code}.\n')
            print(f'Server connection established.')
            self.progressbar_signal.emit()

    @Logging()
    def get_hash_password(self):
        password_bytes = self.client_password.encode('utf-8')
        salt = self.client_login.lower().encode('utf-8')
        password_hash = hashlib.pbkdf2_hmac('sha512', password_bytes, salt, 10000)
        password_hash_string = binascii.hexlify(password_hash)
        return password_hash_string

    @Logging()
    def send_hash_password(self, answer_all):
        answer_data = answer_all[DATA]
        password_hash_string = self.get_hash_password()

        hash = hmac.new(password_hash_string, answer_data.encode('utf-8'))
        digest = hash.digest()
        my_answer = RESPONSE_511
        my_answer[DATA] = binascii.b2a_base64(digest).decode('ascii')

        send_msg(self.connection, my_answer)

    @Logging()
    def connection_lack(self):
        self.is_connected = False
        self.connection_lack_signal.emit()
        exit(1)

    @Logging()
    def load_database(self):
        try:
            users_all = self.get_users_all()
        except (ConnectionResetError, ServerError):
            LOGGER.error('Error requesting list of known users.')
            self.connection_lack()
        else:
            with LOCK_DATABASE:
                self.database.add_known_users(users_all)
                self.mongo_db.add_known_users(users_all)
            print('List of known users updated successfully.')
            self.progressbar_signal.emit()
        try:
            contacts_list = self.get_contacts_all()
        except (ConnectionResetError, ServerError):
            LOGGER.error('Contact list request error.')
            self.connection_lack()
        else:
            with LOCK_DATABASE:
                self.database.add_contacts(contacts_list)
            print('Contact list updated successfully.')
            self.progressbar_signal.emit()
        try:
            groups_list = self.get_groups()
        except (ConnectionResetError, ServerError):
            LOGGER.error('Contact list request error.')
            self.connection_lack()
        else:
            with LOCK_DATABASE:
                self.database.add_groups(groups_list)
            print('Contact list updated successfully.')
            self.progressbar_signal.emit()
        try:
            messages_groups_list = self.get_messages_groups()
        except (ConnectionResetError, ServerError):
            LOGGER.error('Contact list request error.')
            self.connection_lack()
        else:
            with LOCK_DATABASE:
                self.database.add_messages_groups(messages_groups_list)
            print('Contact list updated successfully.')
            self.progressbar_signal.emit()

    @Logging()
    def create_presence_msg(self, account_name, pubkey):
        msg = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: account_name,
                PUBLIC_KEY: pubkey
            }
        }
        return msg

    @Logging()
    def _get_info(self, request):
        LOGGER.debug(f'Formed request {request}')
        with LOCK_SOCKET:
            send_msg(self.connection, request)
            answer = get_msg(self.connection)
        if RESPONSE in answer and answer[RESPONSE] == 202:
            return answer[LIST_INFO]
        else:
            raise ServerError('Invalid server response.')

    @Logging()
    def get_users_all(self):
        LOGGER.debug(f'Request a list of known users {self.client_login}')
        request = {
            ACTION: USERS_REQUEST,
            TIME: time.time(),
            ACCOUNT_NAME: self.client_login
        }
        return self._get_info(request)

    @Logging()
    def get_contacts_all(self):
        LOGGER.debug(f'Request contact sheet for user {self.client_login}.')
        request = {
            ACTION: GET_CONTACTS,
            TIME: time.time(),
            USER: self.client_login
        }
        return self._get_info(request)

    @Logging()
    def get_groups(self):
        LOGGER.debug(f'Request groups for {self.client_login}.')
        request = {
            ACTION: GET_GROUPS,
            TIME: time.time(),
            USER: self.client_login
        }
        return self._get_info(request)

    @Logging()
    def get_messages_groups(self):
        LOGGER.debug(f'Request messages groups for.')
        request = {
            ACTION: GET_MESSAGES_GROUPS,
            TIME: time.time(),
            USER: self.client_login
        }
        return self._get_info(request)

    @Logging()
    def answer_server_presence(self, msg):
        LOGGER.debug(f'Parsing a message from the server - {msg}')
        if RESPONSE in msg:
            if msg[RESPONSE] == 511:
                return 'OK: 511'
            elif msg[RESPONSE] == 200:
                return 'OK: 200'
            elif msg[RESPONSE] == 400:
                LOGGER.info(f'ERROR 400: {msg[ERROR]}')
                raise ServerError(f'{msg[ERROR]}')
            else:
                raise IncorrectCodeError(msg[RESPONSE])
        raise FieldMissingError(RESPONSE)

    @Logging()
    def get_message_from_server(self):
        while True:
            time.sleep(1)
            with LOCK_SOCKET:
                try:
                    message = get_msg(self.connection)
                except IncorrectDataNotDictError:
                    LOGGER.error(f'Failed to decode received message.')
                # Connection timed out if errno = None, otherwise connection break.
                except OSError as err:
                    # print(err.errno)
                    if err.errno:
                        if err.errno != 10038:
                            LOGGER.critical(f'Lost server connection.')
                            self.connection_lost_signal.emit()
                            break
                        else:
                            break
                except (ConnectionError, ConnectionAbortedError, ConnectionResetError,
                        json.JSONDecodeError):
                    LOGGER.critical(f'Lost server connection.')
                    self.connection_lost_signal.emit()
                    break
                else:
                    if ACTION in message and message[ACTION] == MESSAGE \
                            and TO in message and FROM in message \
                            and MESSAGE_TEXT in message and message[TO] == self.client_login:

                        user_login = message[FROM]
                        decrypted_message = self.encrypt_decrypt.message_decryption(message[MESSAGE_TEXT])

                        LOGGER.info(f'Received message from user {user_login}:\n{decrypted_message}.')
                        self.database.save_message(user_login, 'in', decrypted_message)
                        self.new_message_signal_chat.emit(user_login)
                        self.new_message_signal_contacts.emit(user_login)

                    elif ACTION in message and message[ACTION] == MESSAGE_GROUP \
                            and TO in message and FROM in message \
                            and MESSAGE_TEXT in message:
                        with LOCK_DATABASE:
                            self.database.add_group_message(message[TO], message[FROM], message[MESSAGE_TEXT])
                        self.new_message_group_signal.emit(message[TO])

                    elif RESPONSE in message and message[RESPONSE] == 205:
                        with LOCK_DATABASE:
                            self.database.add_known_users(message[LIST_INFO])
                            self.mongo_db.add_known_users(message[LIST_INFO])

                    elif RESPONSE in message and message[RESPONSE] == 206:
                        with LOCK_DATABASE:
                            self.database.add_groups(message[LIST_INFO])
                            self.new_group_signal.emit()
                    else:
                        LOGGER.error(f'Invalid message received from server: {message}')


class ClientTransport:
    """Functions for interacting with the server."""
    def __init__(self, connection, client_login, database, encrypt_decrypt):
        self.connection = connection
        self.client_login = client_login
        self.database = database
        self.encrypt_decrypt = encrypt_decrypt

    @Logging()
    def is_received_pubkey(self, login):
        current_chat_key = self.pubkey_request(login)
        if current_chat_key:
            self.encrypt_decrypt.create_current_encrypt(current_chat_key)
            return True
        return False

    @Logging()
    def pubkey_request(self, login):
        """The function of requesting the public key of the client from the server."""
        LOGGER.debug(f'Public key request for {login}')
        request = {
            ACTION: PUBLIC_KEY_REQUEST,
            TIME: time.time(),
            ACCOUNT_NAME: login
        }
        with LOCK_SOCKET:
            try:
                send_msg(self.connection, request)
                answer = get_msg(self.connection)
            except (OSError, json.JSONDecodeError):
                # self.connection_lost_signal.emit()
                return
        if RESPONSE in answer and answer[RESPONSE] == 511:
            LOGGER.debug(f'Loaded public key for {login}')
            return answer[DATA]
        else:
            LOGGER.error(f'Failed to get the key of the interlocutor {login}. '
                         f'Answer server {answer}')

    @Logging()
    def avatar_request(self, login):
        """The function of requesting the avatar of the client from the server."""
        LOGGER.debug(f'Avatar request for {login}')
        request = {
            ACTION: GET_AVATAR,
            ACCOUNT_NAME: login
        }
        with LOCK_SOCKET:
            try:
                send_msg(self.connection, request)
                answer = get_msg(self.connection)
            except (OSError, json.JSONDecodeError):
                return None
        if RESPONSE in answer and answer[RESPONSE] == 511:
            LOGGER.debug(f'Loaded avatar for {login}')
            img = answer[DATA]
            img_data = base64.b64decode(img)
            filename = get_path_avatar(login)
            with open(filename, 'wb') as f:
                f.write(img_data)
            return True
        elif RESPONSE in answer and answer[RESPONSE] == 400:
            LOGGER.info(f'Answer server {answer[ERROR]}')
        else:
            LOGGER.error(f'Failed to get the avatar {login}. '
                         f'Answer server {answer}')

    @Logging()
    def send_user_message(self, contact_name, message_text):
        encrypted_message = self.encrypt_decrypt.message_encryption(message_text)
        message = {
            ACTION: MESSAGE,
            FROM: self.client_login,
            TO: contact_name,
            TIME: time.time(),
            MESSAGE_TEXT: encrypted_message
        }
        with LOCK_SOCKET:
            try:
                send_msg(self.connection, message)
                answer = get_msg(self.connection)
            except (ConnectionResetError, ConnectionAbortedError, OSError):
                LOGGER.critical('Lost server connection.')
                return False
            else:
                if answer[RESPONSE] == 400:
                    LOGGER.info(f'{answer[ERROR]}. User {contact_name} is offline.')
                    return f'User {contact_name} is offline!'
        LOGGER.debug(f'Message sent: {message},from {self.client_login} username {contact_name}')
        with LOCK_DATABASE:
            self.database.save_message(contact_name, 'out', message_text)
        return True

    @Logging()
    def send_group_message(self, group_name, message_text):
        message = {
            ACTION: MESSAGE_GROUP,
            FROM: self.client_login,
            TO: group_name,
            TIME: time.time(),
            MESSAGE_TEXT: message_text
        }
        with LOCK_SOCKET:
            try:
                send_msg(self.connection, message)
                answer = get_msg(self.connection)
            except (ConnectionResetError, ConnectionAbortedError, OSError):
                LOGGER.critical('Lost server connection.')
                return False
            else:
                if answer[RESPONSE] == 200:
                    LOGGER.info(f'Successfully sent a message for the group {group_name} to the server.')
        with LOCK_DATABASE:
            self.database.add_group_message(group_name, self.client_login, message_text)
        return True

    @Logging()
    def add_contact(self, new_contact_name):
        if self.database.is_user(new_contact_name):
            with LOCK_DATABASE:
                self.database.add_contact(new_contact_name)
            try:
                self.add_contact_server(new_contact_name)
            except ServerError:
                LOGGER.error('Failed to send information to server.')
            except ConnectionResetError:
                LOGGER.error('Server connection lost.')
            else:
                LOGGER.info(f'New contact added {new_contact_name} at the user {self.client_login}.')
                return True
        else:
            LOGGER.error('This user is not registered.')

    @Logging()
    def add_contact_server(self, new_contact_name):
        LOGGER.debug(f'Create a new contact {new_contact_name} at the user {self.client_login}.')
        message = {
            ACTION: ADD_CONTACT,
            TIME: time.time(),
            USER: self.client_login,
            ACCOUNT_NAME: new_contact_name
        }
        with LOCK_SOCKET:
            send_msg(self.connection, message)
            answer = get_msg(self.connection)
        if RESPONSE in answer and answer[RESPONSE] == 200:
            logging.debug(f'Successful contact creation {new_contact_name} at the user {self.client_login}.')
        else:
            raise ServerError('Error creating contact.')

    @Logging()
    def del_contact(self, del_contact_name):
        if self.database.is_contact(del_contact_name):
            with LOCK_DATABASE:
                self.database.del_contact(del_contact_name)
            try:
                self.del_contact_server(del_contact_name)
            except ServerError:
                LOGGER.error('Failed to send information to server.')
            else:
                print(f'Contact {del_contact_name} successfully deleted.')
                return True
        else:
            LOGGER.info('Attempt to delete a nonexistent contact.')

    @Logging()
    def del_contact_server(self, del_contact_name):
        message = {
            ACTION: DELETE_CONTACT,
            TIME: time.time(),
            USER: self.client_login,
            ACCOUNT_NAME: del_contact_name
        }
        with LOCK_SOCKET:
            send_msg(self.connection, message)
            answer = get_msg(self.connection)
        if RESPONSE in answer and answer[RESPONSE] == 200:
            logging.debug(f'Successfully delete a contact {del_contact_name} at the user {self.client_login}')
        else:
            raise ServerError('Client uninstall error.')

    # @Logging()
    def send_avatar_to_server(self):
        with open(get_path_avatar(self.client_login), 'rb') as image_file:
            encoded_img = base64.b64encode(image_file.read()).decode('utf8')

        message = {
            ACTION: SEND_AVATAR,
            USER: {
                ACCOUNT_NAME: self.client_login,
                IMAGE: encoded_img
            }
        }
        with LOCK_SOCKET:
            send_msg(self.connection, message)
            answer = get_msg(self.connection)
        if RESPONSE in answer and answer[RESPONSE] == 200:
            logging.debug(f'Successfully saved avatar.')
        else:
            raise ServerError('Server error. Unsuccessfully saved avatar.')

    @Logging()
    def exit_client(self):
        try:
            send_msg(self.connection, self.create_exit_message(self.client_login))
        except ConnectionResetError:
            LOGGER.critical('Lost server connection.')
            exit(1)
        LOGGER.info('Application shutdown by user command\n.')
        print('Application shutdown by user command.')

    @Logging()
    def create_exit_message(self, client_login):
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: client_login
        }

    @Logging()
    def stop_app(self):
        self.exit_client()
        self.connection.close()


@Logging()
def start_client(client_login, client_password, screen_manager):
    server_ip, server_port = get_args()
    database = ClientDB(client_login)

    # Create Mongo database
    mongo_db = MongoDbClient(client_login)

    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    encrypt_decrypt = EncryptDecrypt(client_login)

    client_transport = ClientTransport(connection, client_login,
                                       database, encrypt_decrypt)

    loading_client = Client(connection, server_ip, server_port,
                            client_login, client_password, database, mongo_db,
                            encrypt_decrypt)
    loading_client.daemon = True
    loading_client.start()

    #  Signals Kivy
    screen_manager.get_screen('loading').connect_loading_signal(loading_client)
    screen_manager.get_screen('chat').connect_chat_signal(loading_client)
    screen_manager.get_screen('contacts').connect_contacts_signal(loading_client)
    return database, client_transport
