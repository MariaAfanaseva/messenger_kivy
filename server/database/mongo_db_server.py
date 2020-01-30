from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime


class MongoDbServer:
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.db_server
        self.all_users = self.db.all_users

    def add_user(self, login, password_hash, fullname=None):
        #  Add user in all users
        self.all_users.insert_one({'login': f'{login}', 'fullname': f'{fullname}',
                                   'password_hash': f'{password_hash}'})


if __name__ == '__main__':
    client = MongoDbServer()
    print(list(client.all_users.find(projection={'login': True, '_id': False})))
