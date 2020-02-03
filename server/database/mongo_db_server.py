from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime


class MongoDbServer:
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.db_server
        self.all_users = self.db.all_users
        self.message_history = self.db.message_history
        self.active_users = self.db.active_users
        self.login_history = self.db.login_history
        self.contacts_users = self.db.contacts_users
        self.groups = self.db.groups
        self.groups_messages = self.db.groups_messages

    def add_user(self, login, password_hash, fullname=None):
        #  Add user in all users
        self.all_users.insert_one({'login': login, 'fullname': fullname,
                                   'password_hash': password_hash,
                                   'last_login': None, 'pubkey': None})

        self.message_history.insert_one({'login': login,
                                         'col_send': 0,
                                         'col_accepted': 0})

    def login_user(self, login, ip_address, port, key):
        now_time = datetime.datetime.now()
        user = self.all_users.find_one({'login': login})
        if user:
            self.all_users.update_one({'login': login},
                                      {'$set': {'last_login': now_time, 'pubkey': key}})
            if user['pubkey'] != key:
                self.all_users.update_one({'login': login},
                                          {'$set': {'pubkey': key}})
        else:
            raise ValueError('Пользователь не зарегистрирован.')

        self.active_users.insert_one({'login': login, 'ip_addr': ip_address,
                                      'port': port,
                                      'login_time': now_time})

        self.login_history.insert_one({'login': login, 'ip_addr': f'{ip_address}',
                                       'port': f'{port}',
                                       'login_time': now_time})

    def remove_user(self, login):
        self.all_users.delete_one({'login': login})
        self.message_history.delete_one({'login': login})
        self.contacts_users.delete_many({'login': login})

    def is_user(self, login):
        if self.all_users.find_one({'login': login}):
            return True
        else:
            return False

    def get_hash(self, login):
        user = self.all_users.find_one({'login': login})
        return user['password_hash']

    def get_pubkey(self, login):
        user = self.all_users.find_one({'login': login})
        return user['pubkey']

    def user_logout(self, login):
        self.active_users.delete_one({'login': login})

    def add_contact(self, user, contact):
        contact_login = self.all_users.find_one({'login': contact})

        if not contact_login or self.contacts_users.find_one({'login': user, 'contact': contact}):
            return

        self.contacts_users.insert_one({'login': user,
                                       'contact': contact})

    def delete_contact(self, user, contact):
        contact_login = self.all_users.find_one({'login': contact})
        if not contact_login:
            return

        self.contacts_users.delete_one({'login': user})

    def sending_message(self, sender, receiver):
        self.message_history.update_one({'login': sender}, {'$inc': {'col_send': 1}})
        self.message_history.update_one({'login': receiver}, {'$inc': {'col_accepted': 1}})

    def get_contacts(self, login_user):
        contacts = list(self.contacts_users.find({'login': login_user}))
        contacts = [contact['contact'] for contact in contacts]
        return contacts

    def users_active_list(self):
        active_users = list(self.active_users.find(projection={'_id': False}))
        active_users = [(user['login'], user['ip_addr'], user['port'], user['login_time'])
                        for user in active_users]
        return active_users

    def history_login(self, login=None):
        history = list(self.login_history.find(projection={'_id': False}))
        if login:
            history = list(self.login_history.find({'login': login}))
        history = [(user['login'], user['ip_addr'], user['port'], user['login_time'])
                   for user in history]

        return history

    def users_all(self):
        users = list(self.all_users.find(projection={'_id': False}))
        users = [(user['login'], user['fullname'], user['last_login'])
                 for user in users]
        return users

    def history_message(self):
        history = list(self.message_history.find(projection={'_id': False}))
        history = [(date['login'], date['col_send'], date['col_accepted'])
                   for date in history]
        return history

    def add_image_path(self, login, img_path):
        self.all_users.update_one({'login': login},
                                  {'$set': {'image': img_path}})

    def add_new_group(self, group_name):
        if not self.is_group(group_name):
            self.groups.insert_one({'group_name': group_name})

    def delete_group(self, group_name):
        if self.is_group(group_name):
            self.groups.delete_one({'group_name': group_name})

    def is_group(self, group_name):
        groups = list(self.groups.find(projection={'group_name': True, '_id': False}))
        groups = [date['group_name'] for date in groups]
        if group_name in groups:
            return True
        else:
            return False

    def get_groups(self):
        groups = list(self.groups.find(projection={'group_name': True, '_id': False}))
        groups = [date['group_name'] for date in groups]
        return groups

    def add_group_message(self, group_name, from_user, message):
        self.groups_messages.insert_one({'group_name': group_name,
                                         'from_user': from_user,
                                         'message': message,
                                         'date': datetime.datetime.now()})

    def get_messages_groups(self):
        messages = list(self.groups_messages.find(projection={'_id': False}))
        messages = [(row['group_name'], row['from_user'], row['message'],
                     row['date'].strftime('%y-%m-%d %H:%M:%S'))
                    for row in messages]
        return messages


if __name__ == '__main__':
    client = MongoDbServer()
    print(list(client.all_users.find(projection={'login': True, '_id': False})))
    print(list(client.contacts_users.find()))
    # print(list(client.active_users.find()))
    # client.add_user('mama', 'ggg')
    # client.remove_user('mama')
    # client.login_user('papa', 'app', '162', '167')
    # client.add_contact('papa', 'mama')
    # client.delete_contact('papa', 'lala')
    # print(list(client.contacts_users.find()))
    # client.sending_message('lala', 'papa')
    # print(list(client.message_history.find()))
    print(client.get_contacts('mari'))
    # client.user_logout('lala')
    # print(client.users_active_list())
    # print(client.history_login('papa'))
    # print(client.history_message())
    # client.delete_group('aa')
    # client.add_new_group('aa')
    # print(client.get_groups())
