import unittest
import sys
import os
import json
from common.utils import send_msg, get_msg
from common.variables import ENCODING, ACTION, PRESENCE, TIME, USER, \
    ACCOUNT_NAME, RESPONSE, ERROR
from common.errors import IncorrectDataNotDictError
sys.path.append(os.path.join(os.getcwd(), '..'))


class TestSocket:
    def __init__(self, test_message):
        self.message = test_message

    def recv(self, max_len):
        json_msg = json.dumps(self.message)
        json_msg_encode = json_msg.encode(ENCODING)
        return json_msg_encode

    def send(self, msg_to_send):
        json_msg = json.dumps(self.message)
        self.encode_json_msg = json_msg.encode(ENCODING)
        self.decode_msg = msg_to_send


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.msg_dict = {
            ACTION: PRESENCE,
            TIME: 1.1,
            USER: {
                ACCOUNT_NAME: 'Python'
            }
        }
        self.msg_dict_200 = {RESPONSE: 200}
        self.msg_dict_400 = {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        }
        self.msg_str = 'Wrong message'

    def test_get_msg(self):
        test_socket_200 = TestSocket(self.msg_dict_200)
        test_socket_400 = TestSocket(self.msg_dict_400)
        self.assertEqual(get_msg(test_socket_200), self.msg_dict_200)
        self.assertEqual(get_msg(test_socket_400), self.msg_dict_400)

    def test_get_msg_wrong(self):
        test_socket = TestSocket(self.msg_str)
        self.assertRaises(IncorrectDataNotDictError, get_msg, test_socket)

    def test_send_msg(self):
        test_socket = TestSocket(self.msg_dict)
        send_msg(test_socket, self.msg_dict)
        self.assertEqual(test_socket.encode_json_msg, test_socket.decode_msg)


if __name__ == '__main__':
    unittest.main()
