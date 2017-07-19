"""Backend based on JSON format using Python dictionaries in memory.
"""
from . import basedb

import os.path
import uuid

import scipy.stats


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

    def create_forest(self, spec, use_complexity=True, use_priority=True):
        spaces = self.split_spec(spec)

        complexity = 1 if use_complexity else None
        priority = 1 if use_priority else None

        for space in spaces:
            tree = self.make_tree(complexity=complexity, priority=priority)
            for s in space:
                leaf = make_space(tree=tree, **s)
                self.add(leaf)
                tree.spaces.append(s)
            self.add(tree)

    def add(self, obj):
        pass

    def query(self, dtype):
        pass

    def remove(self, obj):
        pass

    def make_tree(self, **kwargs):
        return Tree(**kwargs)

    def make_node(self, **kwargs):
        return Node(**kwargs)

    def make_space(self, **kwargs):
        return Space(**kwargs)

    def make_value(self, **kwargs):
        return Value(**kwargs)

    def make_result(self, **kwargs):
        return Result(**kwargs)


class Tree(basedb.BaseTree):
    def __init__(self, complexity=None, priority=None, rank=None, spaces=None,
                 results=None):
        self.id = str(uuid.uuid4())
        self.complexity = complexity
        self.priority = priority,
        self.rank = rank

        self.spaces = spaces if spaces is not None else []
        self.results = results if results is not None else []

    def to_json(self):
        return {
            self.id: {
                'complexity': self.complexity,
                'priority': self.priority,
                'rank': self.rank,
                'spaces': [space.id for space in self.spaces],
                'results': [result.id for result in self.results]
            }
        }


class Space(basedb.BaseSpace):
    def __init__(self, domain=None, path=None, strategy='random',
                 scale='linear', tree=None):
        self.id = str(uuid.uuid4())
        self.domain = domain
        self.path = path
        self.strategy = strategy
        self.scale = scale

        self.tree_id = tree.id if tree is not None else None
        self.tree = tree

    def to_json(self):
        # Handle when the space is defined by a continuous distribution
        if isinstance(self.domain, scipy.stats.rv_continuous):
            rng = self.domain.random_state.get_state()
            domain = {
                'name': self.domain.dist.name,
                'args': list(self.domain.args),
                'kwargs': self.domain.kwds,
                'rng': [
                    rng[0],
                    list(rng[1]),
                    rng[2],
                    rng[3],
                    rng[4]
                ]
            }
        else:
            # Other spaces should be JSON serializable
            domain = self.domain

        return {
            self.id: {
                'domain': domain,
                'path': self.path,
                'strategy': self.strategy,
                'scaling': self.scaling,
                'tree_id': self.tree_id
            }
        }

class Value(basedb.BaseValue):
    def __init__(self, value=None, space=None, result=None):
        self.id = str(uuid.uuid4())
        self.value = value
        self.space_id = space.id if space is not None else None
        self.result_id = result.id if result is not None else None

        self.space = space
        self.result = result

    def to_json(self):
        return {
            self.id: {
                'value': self.value,
                'space_id': self.space_id,
                'result_id': self.result_id
            }
        }


class Result(basedb.BaseResult):
    def __init__(self, loss=None, result=None, tree=None):
        self.id = str(uuid.uuid4)
        self.loss = loss
        self.result = result
        self.tree_id = tree.id if tree is not None else None

        self.tree = tree
