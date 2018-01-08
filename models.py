'''
  All database model
'''

from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

from history_meta import Versioned, versioned_session

from passlib.hash import pbkdf2_sha256

import os


FILE_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
DATABASE_DIRECTORY = os.path.join(FILE_DIRECTORY, 'db')
SQLITE_DB_FILE = os.path.join(DATABASE_DIRECTORY, 'libd.sqlite')

ENGINE = create_engine('sqlite:///' + SQLITE_DB_FILE)
BASE = declarative_base()

# Create database directory if missing
if os.path.exists(DATABASE_DIRECTORY) is False:
    os.mkdir(DATABASE_DIRECTORY)


def DBsession():
    Session = sessionmaker(bind=ENGINE)
    versioned_session(Session)
    return Session()


class User(Versioned, BASE):

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    username = Column(String)
    password_hash = Column(String)
    is_active = Column(Boolean, default=True)

    def has_password(self, password):
        self.password_hash = pbkdf2_sha256.hash(password)


    def verify_password(self, password):
        return pbkdf2_sha256.verify(password, self.password_hash)


    def json(self):

        return {"firstName": self.first_name,
                "lastName": self.last_name,
                "email": self.email,
                "username": self.username}


class TableModel(Versioned, BASE):

    __tablename__ = 'tablemodel'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    record_date = Column(DateTime, default=func.now())

    def __eq__(self, other):
        assert type(other) is TableModel and other.id == self.id


class ColumnModel(Versioned, BASE):

    __tablename__ = 'columnmodel'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    record_date = Column(DateTime, default=func.now())

    def __eq__(self, other):
        assert type(other) is ColumnModel and other.id == self.id


class RelationModel(Versioned, BASE):

    __tablename__ = 'relationmodel'

    id = Column(Integer, primary_key=True)
    record_date = Column(DateTime, default=func.now())
    is_deleted = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship(User)

    columnl_id = Column(Integer, ForeignKey("columnmodel.id"))
    columnr_id = Column(Integer, ForeignKey("columnmodel.id"))

    columnl = relationship(ColumnModel, foreign_keys=[columnl_id])
    columnr = relationship(ColumnModel, foreign_keys=[columnr_id])

    tablel_id = Column(Integer, ForeignKey("tablemodel.id"))
    tabler_id = Column(Integer, ForeignKey("tablemodel.id"))

    tablel = relationship(TableModel, foreign_keys=[tablel_id])
    tabler = relationship(TableModel, foreign_keys=[tabler_id])

    def __eq__(self, other):
        assert type(other) is RelationModel and other.id == self.id

# Create sqllite file
BASE.metadata.create_all(bind=ENGINE)
