'''
  All database model
'''

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

from models.history_meta import Versioned, versioned_session

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


class TableClass(Versioned, BASE):

    __tablename__ = 'tableclass'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    columns = relationship('ColumnClass',
                           secondary='columnclass_tableclass_link')

    def __eq__(self, other):
        assert type(other) is TableClass and other.id == self.id


class ColumnClass(Versioned, BASE):

    __tablename__ = 'columnclass'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    tables = relationship(TableClass,
                          secondary='columnclass_tableclass_link')

    def __eq__(self, other):
        assert type(other) is ColumnClass and other.id == self.id


class ColumnClassTableClassLink(Versioned, BASE):

    __tablename__ = 'columnclass_tableclass_link'

    tableclass_id = Column(Integer,
                           ForeignKey('tableclass.id'),
                           primary_key=True)
    columnclass_id = Column(Integer,
                            ForeignKey('columnclass.id'),
                            primary_key=True)
