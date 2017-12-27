'''
  All database model
'''

from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

from history_meta import Versioned, versioned_session

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
    is_deleted = Column(Boolean, default=False)
    record_date = Column(DateTime, default=func.now())

    def __eq__(self, other):
        assert type(other) is ColumnModel and other.id == self.id


class RelationModel(Versioned, BASE):

    __tablename__ = 'relationmodel'

    id = Column(Integer, primary_key=True)
    record_date = Column(DateTime, default=func.now())
    column_id = Column(Integer, ForeignKey("columnmodel.id"))
    column = relationship(ColumnModel)
    table_id = Column(Integer, ForeignKey("tablemodel.id"))
    table = relationship(TableModel)

    def __eq__(self, other):
        assert type(other) is RelationModel and other.id == self.id

# Create sqllite file
BASE.metadata.create_all(bind=ENGINE)
