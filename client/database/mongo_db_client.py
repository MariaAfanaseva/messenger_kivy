from pymongo import MongoClient
import datetime


class MongoDbClient:
    def __init__(self, login):
        name = f'{login}_db'
        self.client = MongoClient()
        self.db = self.client[name]
        self.users = self.db.users
        self.messages = self.db.messages

    def add_known_users(self, users_all):
        #  users_all - from server
        for user in users_all:
            self.users.insert_one({'login': f'{user}'})

    def get_known_users(self):
        return [login['login'] for login in self.users.find()]

    def save_message(self, contact, direction, message):
        # Message save function
        self.messages.insert_one({'contact': f'{contact}', 'direction': f'{direction}',
                                 'message': f'{message}', 'date': f'{datetime.datetime.now()}'})

    def get_history(self, contact):
        return [(history_row['contact'], history_row['direction'], history_row['message'], history_row['date'])
                for history_row in self.messages.find({'contact': f'{contact}'})]
