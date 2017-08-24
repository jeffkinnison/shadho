from . import basedb

from sqlalchemy import create_engine, Column, Boolean, Float, ForeignKey
from sqlalchemy import Integer, PickleType, Sequence, String, Text
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


BASE = declarative_base()


class SqlBackend(basedb.BaseBackend):
    def __init_(self, url='sqlite:///:memory:'):
        self.engine = create_engine(url, echo=True)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker()
        self.Session.configure(bind=self.engine)

    def add(self, obj):
        if isinstance(obj, (Tree, Space, Value, Result)):
            session = self.Session()
            session.add(obj)
            session.commit()
            session.close()
        else:
            raise InvalidObjectError()

    def get(self, objclass, id):
        if objclass in (Tree, Space, Value, Result):
            session = self.Session()
            obj = session.query(objclass).filter_by(id=id).first()
            session.close()
            return obj
        else:
            raise InvalidObjectClassError

    def make(self, objclass, **kwargs):
        if objclass in (Tree, Space, Value, Result):
            if 'id' in kwargs:
                obj = self.get(objclass, kwargs['id'])

            if obj is None:
                session = self.Session()
                obj = None
                try:
                    obj = objclass(**kwargs)
                    session.add(obj)
                    session.commit()
                except TypeError:
                    raise InvalidObjectError()
                finally:
                    session.close()
            return obj

    def make_forest(self, spec, use_complexity=True, use_priority=True):
        leaves = self.split_spec(spec)

        complexity = 1 if use_complexity else None
        priority = 1 if use_priority else None
        rank = 1 if all([use_complexity, use_priority]) else None

        for leafset in leaves:
            tree = self.make(Tree, complexity=complexity, priority=priority,
                             rank=rank)
            for leaf in leafset:
                space = self.make(Space, tree_id=tree.id, **leaf)
            if use_complexity:
                tree.calculate_complexity()

        return self.update_rank()

    def update_rank(self):
        session = self.Session()
        trees = session.query(Tree).all()

        for tree in trees:
            tree.rank = 1

        try:
            trees.sort(key=lambda x: x.priority, reverse=True)
            for i in range(len(trees)):
                trees[i].rank *= i
        except TypeError:
            pass

        try:
            trees.sort(key=lambda x: x.complexity, reverse=True)
            for i in range(len(trees)):
                trees[i].rank *= i
        except TypeError:
            pass

        session.add_all(trees)
        session.commit()
        session.close()

        return self.order_trees(trees=trees)

    def order_trees(self, trees=None):
        if trees is None:
            session = Session()
            trees = session.query(Tree).all()
            session.close()
        trees.sort(key=lambda x: s.rank)
        return [t.id for t in trees]

    def generate(self, tid):
        session = self.Session()
        tree = session.query(Tree).filter_by(id=tid).first()
        session.close()
        result = self.make(Result, tree_id=tree.id)
        params = {}
        if tree is not None:
            for space in tree.spaces:
                v = space.generate()
                curr = params
                path = space.path.split('/')
                for i in range(len(path) - 1):
                    if path[i] not in curr:
                        curr[path[i]] = {}
                    curr = curr[path[i]]
                curr[path[-1]] = v
                v = self.make(Value, value=v, space_id=space.id,
                              result_id=result.id)
        return (result.id, params)

    def register_result(self, rid, loss, results=None):
        session = self.Session()
        result = session.query(Result).filter_by(id=rid)
        result.loss = loss
        result.results = results
        session.add(result)
        session.commit()
        session.close()
        tree = result.tree

        if len(tree.results) % 10 == 0:
            tree.calculate_priority()
        return self.update_rank()

    def get_optimal(self, mode='global'):
        session = self.Session()
        result = session.query(Result).order_by(Result.loss).first()


class Value(BASE, basedb.BaseValue):
    __tablename__ = 'values'

    id = Column(Integer, Sequence('value_id_seq'), primary_key=True)
    value = Column(PickleType)
    space_id = Column(Integer, ForeignKey('spaces.id'))
    result_id = Column(Integer, ForeignKey('results.id'))

    space = relationship('Space', back_populates='values')
    result = relationship('Result', back_populates='values')


class Result(BASE, basedb.BaseResult):
    __tablename__ = 'results'

    id = Column(Integer, Sequence('result_id_seq'), primary_key=True)
    loss = Column(Float)
    results = Column(PickleType)
    tree_id = Column(Integer, ForeignKey('trees.id'))

    tree = relationship('Tree', back_populates='results')
    values = relationship('Value', order_by=Value.id, back_populates='result')


class Space(BASE, basedb.BaseSpace):
    __tablename__ = 'spaces'

    id = Column(Integer, Sequence('space_id_seq'), primary_key=True)
    domain = Column(PickleType)
    path = Column(Text)
    strategy = Column(String, default='random')
    scaling = Column(String, default='linear')
    tree_id = Column(Integer, ForeignKey('trees.id'))

    tree = relationship('Tree', back_populates='spaces')
    values = relationship('Value', order_by=Value.id, back_populates='space')

class Tree(BASE, basedb.BaseTree):
    __tablename__ = 'trees'

    id = Column(Integer, Sequence('trees_id_seq'), primary_key=True)
    priority = Column(Float)
    complexity = Column(Float)
    rank = Column(Integer)

    spaces = relationship('Space', order_by=Space.id, back_populates='tree')
    results = relationship('Result', order_by=Result.id, back_populates='tree')
