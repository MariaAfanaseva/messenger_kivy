MAX_CONNECTIONS = 3
MAX_PACKAGE_LENGTH = 100000
ENCODING = 'utf-8'
DEFAULT_IP_ADDRESS = '127.0.0.1'
DEFAULT_PORT = 7777
CONFIG_FILE_NAME = 'config_server.ini'

# JIM поля
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
PUBLIC_KEY = 'pubkey'
DATA = 'bin'
RESPONSE = 'response'
ERROR = 'error'
ALERT = 'alert'  # текст сообщения ошибки
ROOM = 'room'  # чат
MESSAGE_TEXT = 'msg_text'
FROM = 'from'
TO = 'to'
IMAGE = 'image'
EXIT = 'exit'

# значения action
PRESENCE = 'presence'  # при подключении к серверу клиента
PROBE = 'probe'  # доступность пользователя online
QUIT = 'quit'  # выход
AUTHENTICATE = 'authenticate'  # авторизация
MESSAGE = 'msg'
JOIN = 'join'  # присоединиться к чату
LEAVE = 'leave'  # покинуть чать
GET_CONTACTS = 'get_contacts'
LIST_INFO = 'data_list'
DELETE_CONTACT = 'del_contact'
ADD_CONTACT = 'add_contact'
USERS_REQUEST = 'get_users'
PUBLIC_KEY_REQUEST = 'get_pubkey'
SEND_AVATAR = 'send_avatar'
GET_AVATAR = 'get_avatar'
GET_GROUPS = 'get_groups'
GET_MESSAGES_GROUPS = 'get_messages_groups'
MESSAGE_GROUP = 'message_group'

# code
BASIC_NOTICE = 100
OK = 200
CREATED = 201  # объект создан
ACCEPTED = 202  # подтверждение
SERVER_ERROR = 500
WRONG_REQUEST = 400  # неправильный запрос

# 200
RESPONSE_200 = {RESPONSE: 200}

# 400
RESPONSE_400 = {
    RESPONSE: 400,
    ERROR: None
}

# 511
RESPONSE_511 = {
    RESPONSE: 511,
    DATA: None
}

# 205
RESPONSE_205 = {
    RESPONSE: 205
}

# 206
RESPONSE_206 = {
    RESPONSE: 206,
    LIST_INFO: None
}


def get_path(name):
    return f'img/avatar_{name}.jpg'
