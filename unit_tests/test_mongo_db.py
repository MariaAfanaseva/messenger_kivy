import unittest
from unittest.mock import Mock, call
from pymongo import MongoClient
from database.mongo_db_client import MongoDbClient


class TestClientMongoDB(unittest.TestCase):
    def setUp(self):
        _client = MongoClient()
        self.test_db = _client.test
        self.db_class = MongoDbClient(self.test_db)

    def test_add_users_known(self):
        self.db_class.add_users_known(['mari', 'lala', 'gala'])
        data = [login['login'] for login in self.db_class.users.find()]
        self.assertEqual(['mari', 'lala', 'gala'], data)

    def test_get_users_known(self):
        self.db_class.add_users_known(['mari', 'lala', 'gala'])
        self.assertEqual(self.db_class.get_users_known(), ['mari', 'lala', 'gala'])

    def tearDown(self):
        self.test_db.command("dropDatabase")


class TestClientDB(unittest.TestCase):
    def test_add_users_known(self):
        client = Mock()
        calls = [call({'login': 'lala'}), call({'login': 'mari'})]
        MongoDbClient.add_users_known(client, ['lala', 'mari'])
        client.users.insert_one.assert_has_calls(calls)


if __name__ == '__main__':
    unittest.main()
