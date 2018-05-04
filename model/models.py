'''
  All database model
'''

import sqlalchemy
from sqlalchemy import (Column,
                        ForeignKey,
                        Integer,
                        String,
                        Boolean,
                        DateTime,
                        types,
                        func)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

from sqlalchemy_continuum import make_versioned

from passlib.hash import pbkdf2_sha256

import os

make_versioned(user_cls=None)

FILE_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
DATABASE_DIRECTORY = os.path.join(FILE_DIRECTORY, '..', 'db')
SQLITE_DB_FILE = os.path.join(DATABASE_DIRECTORY, 'libd.sqlite')

ENGINE = create_engine('sqlite:///' + SQLITE_DB_FILE)
BASE = declarative_base()

# Create database directory if missing
if os.path.exists(DATABASE_DIRECTORY) is False:
    os.mkdir(DATABASE_DIRECTORY)


def DBsession():
    Session = sessionmaker(bind=ENGINE)
    return Session()


class ChoiceType(types.TypeDecorator):
    '''
    SQLAlchemy - How to make "choices" using SQLAlchemy?
    https://stackoverflow.com/a/6264027

    type = Column(ChoiceType([('toto', 'toto'), ('tata', 'tata')]))
    '''

    impl = types.String

    def __init__(self, choices, **kw):
        self.choices = dict(choices)
        super(ChoiceType, self).__init__(**kw)

    def process_bind_param(self, value, dialect):
        return [k for k, v in self.choices.iteritems() if v == value][0]

    def process_result_value(self, value, dialect):
        return self.choices[value]


class User(BASE):

    __versioned__ = {}
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


class TableModel(BASE):

    __versioned__ = {}
    __tablename__ = 'tablemodel'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    record_date = Column(DateTime, default=func.now())

    def __eq__(self, other):
        assert type(other) is TableModel and other.id == self.id


class ColumnModel(BASE):

    __versioned__ = {}
    __tablename__ = 'columnmodel'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    record_date = Column(DateTime, default=func.now())

    def __eq__(self, other):
        assert type(other) is ColumnModel and other.id == self.id


class Meta(BASE):

    __versioned__ = {}
    __tablename__ = 'meta'

    TYPES = [
        (u'description', u'description'),
        (u'related', u'related'),
        (u'tag', u'tag'),
        (u'other', u'other')
    ]

    id = Column(Integer, primary_key=True)
    description = Column(String)
    meta_type = Column(ChoiceType(TYPES))
    is_deleted = Column(Boolean, default=False)
    record_date = Column(DateTime, default=func.now())

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    meta_table_id = Column(Integer, ForeignKey('tablemodel.id'))
    meta_table = relationship(TableModel)

    meta_column_id = Column(Integer, ForeignKey('columnmodel.id'))
    meta_column = relationship(ColumnModel)


    def json(self):

        table_name = None
        column_name = None

        if self.meta_table is not None:
            table_name = self.meta_table.name

        if self.meta_column is not None:
            column_name = self.meta_column.name

        return { "description": self.description,
                 "type": self.meta_type,
                 "user": self.user.json(),
                 "table": table_name,
                 "column_name": column_name,
                 "record_date": self.record_date.strftime('%Y-%m-%d %H:%M:%S')
                }


class RelationModel(BASE):

    __versioned__ = {}
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

sqlalchemy.orm.configure_mappers()
# Create sqllite file
BASE.metadata.create_all(bind=ENGINE)
