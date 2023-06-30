from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, BigInteger, Boolean, Text, VARCHAR

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    ticket_id = Column(VARCHAR, primary_key=True, unique=True, autoincrement=False)  # ticket_id
    tg_id = Column(BigInteger, unique=True, autoincrement=False)  # tg_id
    username = Column(VARCHAR)  # username
    role = Column(VARCHAR, default='visitor')  # role

    def __str__(self):
        return f"""User: tg_id={str(self.tg_id)}, username={self.username}, role={self.role}"""


class Event(Base):
    __tablename__ = 'schedule'

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)  # event_id
    title = Column(Text)  # name
    # position = Column(Integer, unique=True, primary_key=True)  # position
    nomination_id = Column(Integer, autoincrement=False)  # nomination_id

    def __init__(self,
                 id: int = None,
                 title: str = None,
                 # position: int = None,
                 nomination_id: int = None):
        self.id = id
        self.title = title
        # self.position = position
        self.nomination_id = nomination_id

    def __str__(self):
        # return f"""Event: {str(self.id)}, {self.title}, {str(self. position)}, {str(self.nomination_id)}"""
        return f"""Event: {str(self.id)}, {self.title}, {str(self.nomination_id)}"""


class Nomination(Base):
    __tablename__ = 'nominations'

    id = Column(Integer, primary_key=True, unique=True, autoincrement=False)  # nomination_id
    name = Column(Text)  # name


class Vote(Base):
    __tablename__ = 'votes'

    vote_id = Column(Integer, primary_key=True, unique=True, autoincrement=True)  # vote_id
    tg_id = Column(Integer)  # tg_id
    event_id = Column(Integer)  # event_id
    nomination_id = Column(Integer)  # nomination_id

    def __init__(self, tg_id, event_id, nomination_id):
        self.tg_id = tg_id
        self.event_id = event_id
        self.nomination_id = nomination_id


class Settings(Base):
    __tablename__ = 'settings'

    voting_enabled = Column(Boolean, primary_key=True)
    current_event_id = Column(Integer, primary_key=True)

    def __init__(self, voting_enabled, current_event_id):
        self.voting_enabled = voting_enabled
        self.current_event_id = current_event_id
