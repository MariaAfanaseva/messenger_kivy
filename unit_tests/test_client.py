import unittest
from client_main import Client
from common.errors import ServerError, IncorrectCodeError, FieldMissingError
from common.variables import (RESPONSE, RESPONSE_200, RESPONSE_400,
                              RESPONSE_511, ACTION)


class TestClient(unittest.TestCase):
    def setUp(self):
        self.msg_dict_200 = RESPONSE_200
        self.msg_200 = 'OK: 200'
        self.msg_dict_400 = RESPONSE_400
        self.msg_dict_511 = RESPONSE_511
        self.msg_511 = 'OK: 511'
        self.msg_dict_0 = {RESPONSE: 0}
        self.msg_dict_act = {ACTION: 200}

    def test_answer_server_presence(self):
        self.assertEqual(Client.answer_server_presence(None, self.msg_dict_200),
                         self.msg_200)
        self.assertRaises(ServerError, Client.answer_server_presence, None, self.msg_dict_400)
        self.assertEqual(Client.answer_server_presence(None, self.msg_dict_511),
                         self.msg_511)
        self.assertRaises(IncorrectCodeError, Client.answer_server_presence, None, self.msg_dict_0)
        self.assertRaises(FieldMissingError, Client.answer_server_presence, None, self.msg_dict_act)


if __name__ == '__main__':
    unittest.main()
