"""Backend based on JSON format using Python dictionaries in memory.
"""
from . import basedb

import os.path
import uuid
import warnings

import numpy as np
import scipy.stats


class InvalidTableError(Exception):
    pass


class InvalidObjectClassError(Exception):
    pass


class InvalidObjectError(Exception):
    pass


class JSONBackend(basedb.BaseBackend):
    def __init__(self, path='.'):
        self.path = os.path.abspath(path)

        self.db = {
            'trees': {},
            'nodes': {},
            'spaces': {},
            'values': {},
            'results': {}
        }

    def add(self, obj):
        try:
            if isinstance(obj, (Tree, Space, Value, Result)):
                self.db[obj.__tablename__][obj.id] = obj.to_json()
            else:
                raise InvalidObjectClassError()
        except KeyError:
            raise InvalidTableError()
        except AttributeError:
            raise InvalidObjectError()

    def get(self, objclass, id):
        try:
            table = self.db[objclass.__tablename__]
        except KeyError:
            raise InvalidTableError()

        try:
            obj = table[id]
        except KeyError:
            raise InvalidObjectError()

        return objclass(id=id, **obj)

    def make(self, objclass, **kwargs):
        try:
            if objclass.__tablename__ in db:
                obj = objclass(**kwargs)
            else:
                raise InvalidObjectClassError()
        except AttributeError:
            raise InvalidObjectClassError()

        return obj

    def checkpoint(self):
        pass

    def make_forest(self, spec, use_complexity=True, use_priority=True):
        leaves = self.split_spec(spec)

        complexity = 1 if use_complexity else None
        priority = 1 if use_priority else None
        rank = 1 if use_complexity or use_priority else None

        trees = []
        for leafset in leaves:
            tree = self.make(Tree, priority=priority, complexity=complexity,
                             rank=rank)

            for leaf in leafset:
                space = self.make(Space, tree=tree.id, **leaf)
                tree.add_space(space)
                self.add(space)
            if use_complexity:
                tree.calculate_complexity()
            self.add(tree)
            trees.append(tree.id)

        return trees

    def generate(self, tid):
        tree = self.get(tid)
        result = self.make(Result, tree=tree)
        params = {}

        for sid in tree.spaces:
            space = self.get(sid)
            path = space.path.split('/')
            curr = params
            for i in range(len(path) - 1):
                if path[i] not in curr:
                    curr[path[i]] = {}
                curr = curr[path[i]]
            value = self.make(Value,
                              space=space,
                              result=result,
                              value=space.generate())
            curr[path[-1]] = value.value
            self.add(value)

        self.add(result)
        return (result.id, params)

    def register_result(self, rid, loss, results=None):
        result = self.get(rid)
        result.loss = loss
        result.results = results
        self.add(result)

        tree = self.get(result.tree)
        if len(tree.results) % 10 == 0:
            tree.calculate_priority()

    def get_optimal(self, mode='global'):
        pass


class Tree(basedb.BaseTree):
    """Tree of hyperparameter search spaces.

    Parameters
    ----------
    id : str, optional
        The database id of this tree. If not supplied, generated during
        initialization.
    priority : float, optional
        The priority of searching this tree relative to others. If None,
        ignored as a heuristic during the search.
    complexity : float, optional
        The complexity of searching this tree relative to others. If None,
        ignored as a heuristic during the search.
    rank : int, optional
        The order of this tree relative to others in the search, as determined
        by sorting on priority and complexity.
    spaces : list of str or list of `shadho.backend.jsondb.Space`
        The search spaces contained in this tree.
    results : list of str or list of `shadho.backend.jsondb.Result`
        The results observed by testing hyperparameters in this tree.

    Attributes
    ----------
    id : str
        The database id of this tree.
    priority : float
        The priority of searching this tree relative to others.
    complexity : float
        The complexity of searching this tree relative to others.
    rank : int
        The order of this tree relative to others in the search, as determined
        by sorting on priority and complexity.
    spaces : list of str
        The database ids of the search spaces contained in this tree.
    results : list of str
        The database ids of the results observed by testing hyperparameters in
        this tree.
    """
    __tablename__ = 'trees'

    def __init__(self, id=None, priority=None, complexity=None, rank=None,
                 spaces=None, results=None):
        self.id = id if id is not None else str(uuid.uuid4())
        self.priority = priority
        self.complexity = complexity
        self.rank = rank

        self.spaces = []
        spaces = spaces if spaces is not None else []
        for space in spaces:
            self.add_space(space)

        self.results = []
        results = results if results is not None else []
        for result in results:
            self.add_result(result)

    def add_space(self, space):
        """Add a search space to this tree.

        Parameters
        ----------
        space : str or `shadho.backend.jsondb.Space`
            The space to add to this tree.
        """
        if isinstance(space, Space) and isinstance(space.id, str):
            self.spaces.append(space.id)
        elif isinstance(space, str):
            self.spaces.append(space)
        else:
            warnings.warn("Adding invalid space {} to tree {}"
                          .format(space, self.id))

    def add_result(self, result):
        """Add a search space to this tree.

        Parameters
        ----------
        space : str or `shadho.backend.jsondb.Space`
            The space to add to this tree.
        """
        if isinstance(result, Result) and isinstance(result.id, str):
            self.results.append(result.id)
        elif isinstance(result, str):
            self.results.append(result)
        else:
            warnings.warn("Adding invalid result {} to tree {}"
                          .format(result, self.id))

    def to_json(self):
        return {
            'priority': self.priority,
            'complexity': self.complexity,
            'rank': self.rank,
            'spaces': self.spaces,
            'results': self.results,
        }


class Space(basedb.BaseSpace):
    """A hyperparameter search space.

    Parameters
    ----------
    id : str, optional
        The database id of this space. If not supplied, generated during
        initialization.
    domain : `scipy.stats.rv_continuous` or dict or list or constant, optional
        The domain over which to search. If `scipy.stats.rv_continuous`,
        corresponds to a continuous domain. If dict, rebuild a continuous
        domain. Otherwise, the domain is stored directly.
    path : str, optional
        The path down the tree to this space.
    strategy : str, optional
        The name of the search strategy to use.
    scaling : str, optional
        The name of the scaling function to use.
    tree : str or `shadho.backend.jsondb.Tree`, optional
        The tree that this space belongs to.
    values : list of str or list of `shadho.backend.jsondb.Value`, optional
        The values generated from this space, in order.

    Attributes
    ----------
    id : str
        The database id of this space.
    domain : `scipy.stats.rv_continuous` or list or constant
        The domain over which to search.
    path : str
        The path down the tree to this space.
    strategy : str
        The name of the search strategy to use.
    scaling : str
        The name of the scaling function to use.
    tree : str
        The database if of the tree that this space belongs to.
    values : list of str
        The database ids of the values generated from this space, in order.
    """
    __tablename__ = 'spaces'

    def __init__(self, id=None, domain=None, path=None, strategy=None,
                 scaling=None, tree=None, values=None):
        self.id = id if id is not None else str(uuid.uuid4())
        if isinstance(domain, dict):
            distribution = getattr(scipy.stats, domain['distribution'])
            self.domain = distribution(*domain['args'],
                                       **domain['kwargs'])
            rng = np.random.RandomState()
            state = domain['rng']
            rng.set_state(tuple([state[0], np.array(state[1]), *state[2:]]))
            self.domain.random_state = rng
        else:
            self.domain = domain

        self.path = path

        self.strategy = strategy if strategy is not None else 'random'
        self.scaling = scaling if scaling is not None else 'linear'

        if isinstance(tree, Tree):
            self.tree = tree.id
        else:
            self.tree = tree

        self.values = []
        values = values if values is not None else []
        for value in values:
            self.add_value(value)

    def add_value(self, value):
        """Add a value to this search space.

        Parameters
        ----------
        value : str or `shadho.backend.jsondb.Value`
            The value to add to this search space.
        """
        if isinstance(value, Value) and isinstance(value.id, str):
            self.values.append(value.id)
        elif isinstance(value, str):
            self.values.append(value)
        else:
            warnings.warn("Adding invalid result {} to tree {}"
                          .format(value, self.id))

    def to_json(self):
        if hasattr(self.domain, 'dist'):
            rng = self.domain.random_state.get_state()
            domain = {
                'distribution': self.domain.dist.name,
                'args': self.domain.args,
                'kwargs': self.domain.kwds,
                'rng': [rng[0], list(rng[1]), *rng[2:]]
            }
        else:
            domain = self.domain

        return {
            'domain': domain,
            'path': self.path,
            'strategy': self.strategy,
            'scaling': self.scaling,
            'tree': self.tree,
            'values': self.values,
        }


class Value(basedb.BaseValue):
    """A hyperparameter value.

    Parameters
    ----------
    id : str, optional
        The database id of this value. If not supplied, generated during
        initialization.
    value : optional
        The value to store.
    space : str or `shadho.backend.jsondb.Space`
        The space that generated this value.
    result : str or `shadho.backend.jsondb.Result`
        The result obtained from this value.

    Attributes
    ----------
    id : str
        The database id of this value.
    value
        The stored value.
    space : str
        The database id of the space that generated this value.
    result : str
        The database id of the result obtained from this value.
    """
    __tablename__ = 'values'

    def __init__(self, id=None, value=None, space=None, result=None):
        self.id = id if id is not None else str(uuid.uuid4())
        self.value = value
        self.space = space.id if isinstance(space, Space) else space
        self.result = result.id if isinstance(result, Result) else result

    def to_json(self):
        return {
            'value': self.value,
            'space': self.space,
            'result': self.result,
        }


class Result(basedb.BaseResult):
    """A result of testing hyperparameter values.

    Parameters
    ----------
    id : str, optional
        The database id of this result. If not supplied, generated during
        initialization.
    loss : float, optional
        The loss value of this result.
    result : dict, optional
        Additional values to store in this result.
    tree : str or `shadho.backend.jsondb.Tree`, optional
        The tree that this space belongs to.
    values : list of str or list of `shadho.backend.jsondb.Value`, optional
        The values generated from this space, in order.


    Attributes
    ----------
    id : str
        The database id of this result.
    loss : float
        The loss value of this result.
    result : dict
        Additional values to store in this result.
    tree : str
        The database id of the tree that this space belongs to.
    values : list of str
        The dtabase ids of the values generated from this space, in order.
    """
    __tablename__ = 'results'

    def __init__(self, id=None, loss=None, results=None, tree=None,
                 values=None):
        self.id = id if id is not None else str(uuid.uuid4())
        self.loss = loss
        self.results = results
        self.tree = tree.id if hasattr(tree, 'id') else tree

        self.values = []
        if values is not None:
            for value in values:
                if hasattr(value, 'id'):
                    self.values.append(value.id)
                else:
                    self.values.append(value)

    def add_value(self, value):
        """Add a value to this search space.

        Parameters
        ----------
        value : str or `shadho.backend.jsondb.Value`
            The value to add to this search space.
        """
        if isinstance(value, Value) and isinstance(value.id, str):
            self.values.append(value.id)
        elif isinstance(value, str):
            self.values.append(value)
        else:
            warnings.warn("Adding invalid result {} to tree {}"
                          .format(value, self.id))

    def to_json(self):
        return {
            'loss': self.loss,
            'results': self.results,
            'tree': self.tree,
            'values': self.values,
        }
