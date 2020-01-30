import datetime
import re
import asyncio
from sqlalchemy import (create_engine, Column, String, Integer,
                        DateTime, Text, asc, ForeignKey)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class ClientDB:
    """Create tables in database. Interacts with the database of this client"""
    class UsersKnown(Base):
        __tablename__ = 'users_known'
        id = Column(Integer, primary_key=True)
        login = Column(String, unique=True)

        def __init__(self, login):
            self.login = login

        def __repr__(self):
            return "<User(%s)>" % self.login

    class Contacts(Base):
        __tablename__ = 'contacts'
        id = Column(Integer, primary_key=True)
        contact = Column(String, unique=True)

        def __init__(self, contact):
            self.contact = contact

        def __repr__(self):
            return "<Contact(%s)>" % self.contact

    class HistoryMessages(Base):
        __tablename__ = 'history_messages'
        id = Column(Integer, primary_key=True)
        contact = Column(String)
        direction = Column(String)
        message = Column(Text)
        date = Column(DateTime)

        def __init__(self, contact, direction, message, date):
            self.contact = contact
            self.direction = direction
            self.message = message
            self.date = date

        def __repr__(self):
            return "<User('%s','%s', '%s, '%s')>" % \
                   (self.contact, self.direction, self.message, self.date)

    class Groups(Base):
        __tablename__ = 'groups'
        group_id = Column(Integer, primary_key=True)
        group_name = Column(String, unique=True)

        def __init__(self, group_name):
            self.group_name = group_name

        def __repr__(self):
            return "<Group('%s','%s)>" % \
                   (self.group_id, self.group_name)

    class GroupsMessages(Base):
        __tablename__ = 'groups_messages'
        id = Column(Integer, primary_key=True)
        group_id = Column(ForeignKey('groups.group_id'))
        from_user = Column(String)
        message = Column(Text)
        date = Column(DateTime)

        def __init__(self, group_id, from_user, message, date):
            self.group_id = group_id
            self.from_user = from_user
            self.message = message
            self.date = date

        def __repr__(self):
            return "<Group messages('%s','%s, '%s','%s)>" % \
                   (self.group_id, self.from_user, self.message, self.date)

    def __init__(self, login):
        # echo - logging, 7200 - seconds restart connect
        self.login = login
        self.database_engine = create_engine(f'sqlite:///client_{self.login}.db3',
                                             echo=False, pool_recycle=7200,
                                             connect_args={'check_same_thread': False})
        Base.metadata.create_all(self.database_engine)
        Session = sessionmaker(bind=self.database_engine)
        self.session = Session()

    def add_contacts(self, contacts_list):
        #  contacts-list - contact list from server
        self.session.query(self.Contacts).delete()
        self.session.commit()
        for contact in contacts_list:
            self.add_contact(contact)

    def add_known_users(self, users_all):
        #  users_all - from server
        self.session.query(self.UsersKnown).delete()
        for user in users_all:
            user_new = self.UsersKnown(user)
            self.session.add(user_new)
        self.session.commit()

    def get_known_users(self):
        return [user[0] for user in self.session.query(self.UsersKnown.login).all()]

    def add_contact(self, contact):
        if not self.session.query(self.Contacts).filter_by(contact=contact).count():
            contact = self.Contacts(contact)
            self.session.add(contact)
            self.session.commit()

    def del_contact(self, contact):
        self.session.query(self.Contacts).filter_by(contact=contact).delete()

    def get_contacts(self):
        return [user[0] for user in self.session.query(self.Contacts.contact).all()]

    def is_user(self, login):
        if self.session.query(self.UsersKnown).filter_by(login=login).count():
            return True
        return False

    def is_contact(self, contact):
        if self.session.query(self.Contacts).filter_by(contact=contact).count():
            return True
        else:
            return False

    def save_message(self, contact, direction, message):
        # Message save function
        message_row = self.HistoryMessages(contact, direction, message, datetime.datetime.now())
        self.session.add(message_row)
        self.session.commit()

    def get_history(self, contact):
        # Function returning correspondence history
        query = self.session.query(self.HistoryMessages).filter_by(contact=contact)
        return [(history_row.contact, history_row.direction, history_row.message, history_row.date)
                for history_row in query.all()]

    def get_search_contact(self, login):
        """ Search contact in Contacts"""
        contacts = self.session.query(self.Contacts.contact).filter(self.Contacts.contact.ilike(f'%{login}%'))
        return [contact[0] for contact in contacts.all()]

    def async_search_message(self, contact, text):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        task = loop.create_task(self.get_search_message(contact, text))
        result = loop.run_until_complete(task)
        loop.close()
        return result

    def async_search_message_group(self, group_name, text):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        task = loop.create_task(self.get_search_message_group(group_name, text))
        result = loop.run_until_complete(task)
        loop.close()
        return result

    @staticmethod
    async def _search_in_html(query, text):
        messages = []
        for history_row in query.all():
            html_message = history_row.message
            matches = re.findall(r'>[^<>]+</p|>[^<>]+</span', html_message)
            for message in matches:
                if text.lower() in message.lower():
                    messages.append(history_row)
                    break
        return messages

    async def get_search_message(self, contact, text):
        """Search message in history"""
        query = self.session.query(self.HistoryMessages).\
            filter(self.HistoryMessages.contact.like(f'{contact}'),
                   self.HistoryMessages.message.ilike(f'%{text}%'))
        query = query.order_by(asc(self.HistoryMessages.date))  # sort by date
        messages = await self._search_in_html(query, text)
        return [(history_row.contact, history_row.direction, history_row.message, history_row.date)
                for history_row in messages]

    async def get_search_message_group(self, group_name, text):
        """Search message in history group"""
        group_id = self.session.query(self.Groups).filter_by(group_name=group_name).first().group_id
        query = self.session.query(self.GroupsMessages).\
            filter_by(group_id=group_id).\
            filter(self.GroupsMessages.message.ilike(f'%{text}%'))
        query = query.order_by(asc(self.GroupsMessages.date))  # sort by date
        messages = await self._search_in_html(query, text)
        return [(history_row.from_user, history_row.message, history_row.date)
                for history_row in messages]

    def add_group(self, group):
        if not self.session.query(self.Groups).filter_by(group_name=group).count():
            group = self.Groups(group)
            self.session.add(group)
            self.session.commit()

    def add_groups(self, groups_list):
        #  groups-list - groups list from server
        self.session.query(self.Groups).delete()
        self.session.commit()
        for group in groups_list:
            self.add_group(group)

    def get_groups(self):
        return [group[0] for group in self.session.query(self.Groups.group_name).all()]

    def get_messages_group(self, group_name):
        # Function returning messages group
        group_id = self.session.query(self.Groups).filter_by(group_name=group_name).first().group_id
        query = self.session.query(self.GroupsMessages).filter_by(group_id=group_id)
        return [(history_row.from_user, history_row.message, history_row.date)
                for history_row in query.all()]

    def add_messages_groups(self, messages_groups_list):
        #  messages_groups_list - from server
        self.session.query(self.GroupsMessages).delete()
        for message in messages_groups_list:
            message_new = self.GroupsMessages(group_id=message[0],
                                              from_user=message[1],
                                              message=message[2],
                                              date=datetime.datetime.strptime(message[3], '%y-%m-%d %H:%M:%S'))
            self.session.add(message_new)
        self.session.commit()

    def add_group_message(self, group_name, from_user, message):
        group_id = self.session.query(self.Groups).filter_by(group_name=group_name).first().group_id
        new_message = self.GroupsMessages(group_id, from_user, message, date=datetime.datetime.now())
        self.session.add(new_message)
        self.session.commit()
