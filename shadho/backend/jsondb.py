"""Backend based on JSON format using Python dictionaries in memory.
"""
from shadho.backend import basedb
from shadho.heuristics import priority

from collections import OrderedDict
import json
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
    """Data management and storage backend based on JSON.

    Parameters
    ----------
    path : str, optional
        Path to the directory to write data.

    Attributes
    ----------
    path : str
        Path to the directory to write data.
    db : dict
        In-memory dictionary containing search data.

    """

    def __init__(self, path='.'):
        self.path = os.path.abspath(os.path.expanduser(path))

        self.db = {
            'trees': {},
            'spaces': {},
            'values': {},
            'results': {},
        }
        
        self.spaces = {}

    def add(self, obj):
        """Add an object to the database.

        Parameters
        ----------
        obj : `Tree` or `Space` or `Value` or `Result`

        Raises
        ------
        InvalidObjectClassError
            If the object provided is not an instance of `Tree` or `Space` or
            `Value` or `Result`.
        InvalidTableError
            If the table name referenced in ``obj`` does not exist in the
            database.
        InvalidObjectError
            If ``obj`` does not have the correct interface.

        Notes
        -----
        If the object already exists in the database (i.e., by id lookup), the
        existing record will be updated.
        """
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
        """Retrieve an object from the database by id.

        Parameters
        ----------
        objclass
            The class of object to retrieve, one of `Tree` or `Space` or
            `Value` or `Result`.
        id : str
            The id to look up.

        Returns
        -------
        The instance of ``objclass`` referenced by ``id``.

        Raises
        ------
        InvalidObjectClassError
            If ``objclass`` is not one of `Tree` or `Space` or `Value` or
            `Result`.
        InvalidObjectError
            If a record with ``id`` does not exist in the referenced table.
        """
        try:
            if objclass in (Tree, Space, Value, Result):
                table = self.db[objclass.__tablename__]
            else:
                raise InvalidObjectClassError()
        except KeyError:
            raise InvalidTableError()

        try:
            obj = table[id]
        except KeyError:
            raise InvalidObjectError()

        return objclass(id=id, **obj)

    def make(self, objclass, **kwargs):
        """Create an object from a set of keyword parameters.

        Parameters
        ----------
        objclass
            The class of object to retrieve, one of `Tree` or `Space` or
            `Value` or `Result`.

        Returns
        -------
            An instance of ``objclass``.

        Notes
        -----
        The created object's state will be set to the passed keywords. See the
        initializations for `Tree`, `Space`, `Value`, and `Result`.

        See Also
        --------
        `shadho.backend.jsondb.Tree`
        `shadho.backend.jsondb.Space`
        `shadho.backend.jsondb.Value`
        `shadho.backend.jsondb.Result`
        """
        try:
            if objclass.__tablename__ in self.db:
                obj = objclass(**kwargs)
            else:
                print(objclass.__tablename__)
                raise InvalidObjectClassError()
        except AttributeError:
            raise InvalidObjectClassError()

        return obj

    def checkpoint(self):
        """Save the database to file.
        """
        with open(os.path.join(self.path, 'shadho.json'), 'w') as f:
            json.dump(self.db, f)

    def make_forest(self, spec, use_complexity=True, use_priority=True):
        """Set up the forest of hyperparameter search spaces.

        Parameters
        ----------
        spec : dict
            The forest specification.
        use_complexity : bool, optional
            If True, initialize the forest to use the complexity heuristic.
        use_priority : bool, optional
            If True, initialize the forest to use the priority heuristic.

        Returns
        -------
        trees : list of str
            The ids of each tree in the forest. If ``use_complexity`` is True,
            ids are ordered by tree complexity.
        """
        leaves = self.split_spec(spec)

        complexity = 1 if use_complexity else None
        priority = [1] if use_priority else None
        rank = 1 if use_complexity or use_priority else None

        trees = []
        for leafset in leaves:
            tree = self.make(Tree, priority=priority, complexity=complexity,
                             rank=rank)
            t_comp = 0
            for leaf in leafset:
                space = self.make(Space, tree=tree.id, **leaf)
                tree.add_space(space)
                self.add(space)
                self.spaces[space.id] = space
                if use_complexity:
                    t_comp += space.complexity
            tree.complexity = t_comp if use_complexity else None
            tree.spaces = sorted(tree.spaces)
            self.add(tree)
            trees.append(tree.id)

        return self.update_rank(trees)

    def order_trees(self, trees=None):
        """Order the trees in the forest by their rank.

        Returns
        -------
        trees : list of str
            The id of each tree in the forest, ordered by ``Tree.rank``.
        """
        if trees is None:
            trees = [tid for tid in self.db['trees']]
        if self.db['trees'][trees[0]]['rank'] is not None:
            trees.sort(key=lambda x: self.db['trees'][x]['rank'])
            for i in range(len(trees)):
                self.db['trees'][trees[i]]['rank'] = i
        return trees

    def update_rank(self, trees=None):
        """Update the rank of the treesby complexity and priority heuristics.

        Parameters
        ----------
        trees : list of str, optional
            The list of tree ids. Loaded from the database if not provided.

        Returns
        -------
        The list of tree ids, sorted by ``Tree.rank``.
        """
        if trees is None:
            trees = [tid for tid in self.db['trees']]

        for tree in trees:
            self.db['trees'][tree]['rank'] = 1 if self.db['trees'][tree]['rank'] is not None else None

        if self.db['trees'][trees[0]]['priority'] is not None:
            trees.sort(key=lambda x: self.db['trees'][x]['priority'][-1],
                       reverse=True)
            for i in range(len(trees)):
                self.db['trees'][trees[i]]['rank'] *= i

        if self.db['trees'][trees[0]]['complexity'] is not None:
            trees.sort(key=lambda x: self.db['trees'][x]['complexity'],
                       reverse=True)
            for i in range(len(trees)):
                self.db['trees'][trees[i]]['rank'] *= i

        return self.order_trees(trees)

    def generate(self, tid):
        """Generate hyperparameter values.

        Parameters
        ----------
        tid : str
            The id of the tree to generate from.

        Returns
        -------
        params : dict
            The generated hyperparameter values, structured in the same shape
            as the `Tree` instance referenced by ``id``.

        Notes
        -----
        The tree structure is created by nesting dictionaries, with each
        hyperparameter value stored at the first key in a path down the tree
        that is not a dictionary.
        """
        tree = self.get(Tree, tid)
        result = self.make(Result, tree=tree)
        params = {}

        for sid in tree.spaces:
            space = self.spaces[sid]
            path = space.path.split('/')
            value = self.make(Value,
                              space=space,
                              result=result,
                              value=space.generate())
            if len('path') > 0 and path[0] != '':
                curr = params
                for i in range(len(path) - 1):
                    if path[i] not in curr:
                        curr[path[i]] = {}
                    curr = curr[path[i]]
                curr[path[-1]] = value.value
            elif len(path) == 1 and path[0] == '':
                params = value.value
            else:
                params = None
            self.add(value)
            result.add_value(value)
            space.add_value(value)
            self.add(space)

        self.add(result)
        return (result.id, params)

    def register_result(self, rid, loss, results=None):
        """
        """
        result = self.get(Result, rid)

        if loss is None:
            params = {}
            for vid in result.values:
                value = self.get(Value, vid)
                space = self.spaces[value.space]
                curr = params
                path = space.path.split('/')
                for i in range(len(path) - 1):
                    if path[i] not in curr:
                        curr[path[i]] = {}
                    curr = curr[path[i]]
                curr[path[-1]] = value.value
            result.submissions += 1
            self.add(result)
            return (result.submissions, params)

        result = self.get(Result, rid)
        result.loss = loss
        result.results = results
        self.add(result)

        tree = self.get(Tree, result.tree)
        tree.add_result(result)
        update = False
        if tree.priority is not None and len(tree.results) % 10 == 0:
            self.calculate_priority(tree)
            update = True
        self.add(tree)
        return update

    def calculate_priority(self, tree):
        feats = np.zeros((len(tree.results), len(tree.spaces)),
                         dtype=np.float64)
        losses = np.zeros((len(tree.results)), dtype=np.float64)

        spaces = {}

        for i in range(len(tree.results)):
            result = self.db['results'][tree.results[i]]
            losses[i] += result['loss']
            
            for j in range(len(self.db['results'][tree.results[i]]['values'])):
                value = self.db['values'][result['values'][j]]
                if value['space'] not in spaces:
                    spaces[value['space']] = self.get(Space, value['space'])
                feats[i][j] += spaces[value['space']].get_label(value['value'])
        
        tree.priority.append(priority(feats, losses.transpose()))

    def get_optimal(self, mode='global'):
        opt = None
        loss = None
        params = {}
        for r in self.db['results']:
            l = self.db['results'][r]['loss']
            if opt is None or (l is not None and loss is not None and l < loss):
                opt = r
                loss = self.db['results'][opt]['loss']

        opt = self.get(Result, opt)
        for v in opt.values:
            value = self.get(Value, v)
            space = self.spaces[value.space]
            path = space.path.split('/')
            curr = params
            for i in range(len(path) - 1):
                if path[i] not in curr:
                    curr[path[i]] = {}
                curr = curr[path[i]]
            curr[path[-1]] = value.value

        return(opt.loss, params, opt.results)


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
        if isinstance(priority, int):
            self.priority = [priority]
        else:
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
                 scaling=None, tree=None, values=None, exhaustive=False,
                 exhaustive_idx=None):
        self.id = id if id is not None else str(uuid.uuid4())
        self.exhaustive_idx = exhaustive_idx
        if isinstance(domain, dict):
            distribution = getattr(scipy.stats, domain['distribution'])
            self.domain = distribution(*domain['args'],
                                       **domain['kwargs'])
            rng = np.random.RandomState()
            if 'rng' in domain:
                state = domain['rng']
                rng.set_state(tuple([state[0], np.array(state[1]), state[2],
                                     state[3], state[4]]))
            self.domain.random_state = rng
        elif exhaustive and isinstance(domain, list) and exhaustive_idx is None:
            self.domain = domain
            self.exhaustive_idx = 0
        else:
            self.domain = domain

        self.exhaustive = exhaustive

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
                'rng': [rng[0], rng[1].tolist(), rng[2], rng[3], rng[4]]
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
            'exhaustive': self.exhaustive,
            'exhaustive_idx': self.exhaustive_idx,
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
    submissions : int, optional
        The number of times this result has been submitted for processing.

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
    submissions : int
        The number of times this result has been submitted for processing.
    """
    __tablename__ = 'results'

    def __init__(self, id=None, loss=None, results=None, submissions=None,
                 tree=None, values=None):
        self.id = id if id is not None else str(uuid.uuid4())
        self.loss = loss
        self.results = results
        self.submissions = submissions if submissions is not None else 0
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
