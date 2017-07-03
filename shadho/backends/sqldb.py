"""Bindings for a SQL database backend.
"""
from .base import BaseBackend

from sqlalchemy import create_engine
from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, PickleType
from sqlalchemy import Sequence, String, Text, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship, sessionmaker

BASE = declarative_base()


class InvalidObjectType(Exception):
    pass


class SQLBackend(BaseBackend):
    """
    """

    def __init__(self, url):
        self.engine = create_engine(url)
        self.session = sessionmaker(bind=self.engine)

    def add(self, obj):
        if isinstance(obj, (Experiment, Tree, Node, Space, Value, Result)):
            self.session.add(obj)
            self.session.commit()
        else:
            raise InvalidObjectType('{} is not a valid object for this backend'
                                    .format(obj))

    def query(self, orm_type):
        if orm_type in (Experiment, Tree, Node, Space, Value, Result):
            return self.session.query(orm_type)
        else:
            raise InvalidObjectType('{} is not a valid type for this backend'
                                    .format(obj))

    def delete(self, obj):
        if isinstance(obj, (Experiment, Tree, Node, Space, Value, Result)):
            self.session.delete(obj)
            self.session.commit()
        else:
            raise InvalidObjectType('{} is not a valid object for this backend'
                                    .format(obj))


# class Experiment(BASE):
#     __tablename__ = 'experiments'
#
#     id = Column(Integer, Sequence('exp_id_seq'), primary_key=True)
#     name = Column(String(256))
#     owner = Column(String(256))
#     created_on = Column(TIMESTAMP)
#     description = Column(Text)


class Tree(BASE):
    __tablename__ = 'trees'

    id = Column(Integer, Sequence('tree_id_seq'), primary_key=True)
    #experiment = Column(Integer, ForeignKey('experiments.id'))
    root_id = Column(Integer, ForeignKey('nodes.id'))
    priority = Column(Float)
    complexity = Column(Float)
    rank = Column(Integer)

    root = relationship('Node', uselist=False)
    results = relationship('Result', back_populates='tree')


class Node(BASE):
    __tablename__ = 'nodes'

    id = Column(Integer, Sequence('node_id_seq'), primary_key=True)
    name = Column(String(256))
    parent_id = Column(Integer, ForeignKey('nodes.id'))
    space_id = Column(Integer, ForeignKey('spaces.id'), nullable=True)
    exclusive = Column(Boolean)
    optional = Column(Boolean)

    space = relationship('Space', back_populates='node')
    children = relationship('Node',
                            backref=backref('parent', remote_side=[id])
                            )


class Space(BASE):
    __tablename__ = 'spaces'

    id = Column(Integer, Sequence('space_id_seq'), primary_key=True)
    node_id = Column(Integer, ForeignKey('nodes.id'))
    space = Column(PickleType)
    scaling = Column(String(256))
    strategy = Column(String(256))

    node = relationship('Node', back_populates='space')


class Value(BASE):
    __tablename__ = 'values'

    id = Column(Integer, Sequence('value_id_seq'), primary_key=True)
    node = Column(Integer, ForeignKey('nodes.id'))
    result_id = Column(Integer, ForeignKey('results.id'))
    val = Column(PickleType)

    result = relationship('Result', back_populates='values')

class Result(BASE):
    __tablename__ = 'results'

    id = Column(Integer, Sequence('result_id_seq'), primary_key=True)
    tree_id = Column(Integer, ForeignKey('trees.id'))
    loss = Column(Float)
    result = Column(PickleType)

    tree = relationship('Tree', back_populates='results')
    values = relationship('Value', back_populates='result')
