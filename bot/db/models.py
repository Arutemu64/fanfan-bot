from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, BigInteger, Boolean, Text, VARCHAR

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    ticket_id = Column(VARCHAR, primary_key=True, unique=True, autoincrement=False)  # ticket_id
    tg_id = Column(BigInteger, unique=True, autoincrement=False)  # tg_id
    username = Column(VARCHAR)  # username
    role = Column(VARCHAR, default='visitor')  # role
    notifications_enabled = Column(Boolean, default=False)  # notifications_enabled

    def __str__(self):
        return f"""User: tg_id={str(self.tg_id)}, username={self.username}, role={self.role}"""


class Performance(Base):
    __tablename__ = 'schedule'

    # event_id = Column(Integer, primary_key=True, unique=True, autoincrement=True)  # event_id
    position = Column(Integer, unique=True, primary_key=True)  # position
    name = Column(Text)  # name
    # duration = Column(Integer)  # duration
    nomination_id = Column(Integer, autoincrement=False)  # nomination_id
    current = Column(Boolean, default=False)

    def __init__(self, position=None, nomination_id=None, name=None):
        self.position = position
        self.name = name
        self.nomination_id = nomination_id


class Nomination(Base):
    __tablename__ = 'nominations'

    id = Column(Integer, primary_key=True, unique=True, autoincrement=False)  # nomination_id
    name = Column(Text)  # name


class Vote(Base):
    __tablename__ = 'votes'

    vote_id = Column(Integer, primary_key=True, unique=True, autoincrement=True)  # vote_id
    tg_id = Column(Integer)  # tg_id
    position = Column(Integer)  # position
    nomination_id = Column(Integer)  # nomination_id

    def __init__(self, tg_id, position, nomination_id):
        self.tg_id = tg_id
        self.position = position
        self.nomination_id = nomination_id


class Settings(Base):
    __tablename__ = 'settings'

    voting_enabled = Column(Boolean, primary_key=True)
