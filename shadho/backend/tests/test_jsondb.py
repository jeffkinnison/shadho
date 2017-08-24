import pytest

from shadho.backend.jsondb import JSONBackend, Tree, Space, Value, Result
from shadho.backend.jsondb import InvalidTableError, InvalidObjectClassError
from shadho.backend.jsondb import InvalidObjectError

from shadho.heuristics import complexity

from test_basedb import TestBaseBackend, TestBaseTree, TestBaseSpace
from test_basedb import TestBaseValue, TestBaseResult

from collections import OrderedDict
import os
import uuid

import numpy as np
import scipy.stats


class TestJSONBackend(TestBaseBackend):
    __testbackend__ = JSONBackend
    __testtree__ = Tree
    __testspace__ = Space
    __testvalue__ = Value
    __testresult__ = Result

    def test_init(self):
        # Test defaults
        b = self.__testbackend__()
        assert b.path == os.getcwd()
        assert b.db == {'trees': {}, 'spaces': {}, 'values': {}, 'results': {}}

        # Test with custom absolute path
        b = self.__testbackend__(path='/tmp/shadho')
        assert b.path == '/tmp/shadho'
        assert b.db == {'trees': {}, 'spaces': {}, 'values': {}, 'results': {}}

        # Test with custom relative path
        b = self.__testbackend__(path='~/shadho')
        p = os.path.expanduser('~/shadho')
        assert b.path == p
        assert b.db == {'trees': {}, 'spaces': {}, 'values': {}, 'results': {}}

    def test_add(self):
        b = self.__testbackend__()

        # Add a Tree
        t = self.__testtree__()
        tdb = {
            'complexity': None,
            'priority': None,
            'rank': None,
            'spaces': [],
            'results': [],
        }
        b.add(t)
        assert t.id in b.db['trees']
        assert b.db['trees'][t.id] == tdb
        assert b.db['trees'][t.id] == t.to_json()

        # Add a Space
        s = self.__testspace__()
        sdb = {
            'domain': None,
            'path': None,
            'strategy': 'random',
            'scaling': 'linear',
            'tree': None,
            'values': []
        }
        b.add(s)
        assert s.id in b.db['spaces']
        assert b.db['spaces'][s.id] == sdb
        assert b.db['spaces'][s.id] == s.to_json()

        # Add a Value
        v = self.__testvalue__()
        vdb = {
            'value': None,
            'space': None,
            'result': None
        }
        b.add(v)
        assert v.id in b.db['values']
        assert b.db['values'][v.id] == vdb
        assert b.db['values'][v.id] == v.to_json()

        # Add a Result
        r = self.__testresult__()
        rdb = {
            'loss': None,
            'results': None,
            'tree': None,
            'values': []
        }
        b.add(r)
        assert r.id in b.db['results']
        assert b.db['results'][r.id] == rdb
        assert b.db['results'][r.id] == r.to_json()

        # Ensure that the database contains all of the correct information
        db = {
            'trees': {t.id: tdb},
            'spaces': {s.id: sdb},
            'values': {v.id: vdb},
            'results': {r.id: rdb},
        }
        assert b.db == db

        # Test throwing exceptions
        with pytest.raises(InvalidObjectClassError):
            b.add(3245)

        with pytest.raises(InvalidTableError):
            t = self.__testtree__()
            t.__tablename__ = 'foo'
            b.add(t)

        t.__tablename__ = 'trees'

        with pytest.raises(InvalidObjectError):
            r = self.__testresult__()
            del r.id
            b.add(r)

    def test_get(self):
        t = self.__testtree__()
        s = self.__testspace__()
        v = self.__testvalue__()
        r = self.__testresult__()

        b = self.__testbackend__()
        b.add(t)
        b.add(s)
        b.add(v)
        b.add(r)

        # Test getting each class of object
        t2 = b.get(Tree, t.id)
        assert t.id == t2.id
        assert t.to_json() == t2.to_json()

        s2 = b.get(Space, s.id)
        assert s.id == s2.id
        assert s.to_json() == s2.to_json()

        v2 = b.get(Value, v.id)
        assert v.id == v2.id
        assert v.to_json() == v2.to_json()

        r2 = b.get(Result, r.id)
        assert r.id == r2.id
        assert r.to_json() == r2.to_json()

        # Test getting invalid objects
        with pytest.raises(InvalidObjectClassError):
            b.get(JSONBackend, 'foo')

        with pytest.raises(InvalidTableError):
            Tree.__tablename__ = 'foo'
            b.get(Tree, t.id)

        Tree.__tablename__ = 'trees'

        with pytest.raises(InvalidObjectError):
            b.get(Result, 'foo')

    def test_make(self):
        b = self.__testbackend__()

        # Test making Trees
        t1 = b.make(self.__testtree__)
        assert isinstance(t1, self.__testtree__)
        assert hasattr(t1, 'id')
        assert t1.priority is None
        assert t1.complexity is None
        assert t1.rank is None
        assert t1.spaces == []
        assert t1.results == []

        tid = str(uuid.uuid4())
        t2 = b.make(Tree, id=tid, complexity=1, priority=1, rank=1,
                    spaces=['1', '2', '3', '4', '5'],
                    results=['6', '7', '8', '9', '10'])
        assert t2.id == tid
        assert t2.priority == 1
        assert t2.complexity == 1
        assert t2.rank == 1
        assert t2.spaces == ['1', '2', '3', '4', '5']
        assert t2.results == ['6', '7', '8', '9', '10']

        # Test making Spaces
        s = b.make(self.__testspace__)
        assert hasattr(s, 'id')
        assert s.domain is None
        assert s.strategy == 'random'
        assert s.scaling == 'linear'
        assert s.tree is None
        assert s.values == []

        t = self.__testtree__()
        v = self.__testvalue__()
        sid = str(uuid.uuid4())
        s = b.make(self.__testspace__, id=sid, domain=1, strategy='tpe', scaling='ln', tree=t,
                  values=[v])
        assert s.id == sid
        assert s.domain == 1
        assert s.strategy == 'tpe'
        assert s.scaling == 'ln'
        assert s.tree == t.id
        assert s.values == [v.id]

        s = b.make(self.__testspace__, id=sid, domain=[1, 2, 3, 4], tree=t.id, values=[v.id])
        assert s.domain == [1, 2, 3, 4]
        assert s.tree == t.id
        assert s.values == [v.id]

        dist = scipy.stats.uniform(loc=-7, scale=42)
        s = b.make(self.__testspace__, domain=dist)
        assert s.domain is dist

        rng = np.random.RandomState().get_state()
        domain = {
            'distribution': 'uniform',
            'args': [],
            'kwargs': {
                'loc': -7,
                'scale': 42,
            },
            'rng': [rng[0], list(rng[1]), rng[2], rng[3], rng[4]]
        }
        s = b.make(self.__testspace__, domain=domain)
        assert s.domain.dist.name == 'uniform'
        assert s.domain.args == ()
        assert s.domain.kwds == {'loc': -7, 'scale': 42}
        state = s.domain.random_state.get_state()
        assert state[0] == rng[0]
        assert np.all(state[1] == np.array(rng[1]))
        assert state[2] == rng[2]
        assert state[3] == rng[3]
        assert state[4] == rng[4]

        # Test making Values
        v = b.make(self.__testvalue__)
        assert hasattr(v, 'id')
        assert v.value is None
        assert v.space is None
        assert v.value is None

        vid = str(uuid.uuid4())
        s = self.__testspace__()
        r = self.__testresult__()

        v = b.make(self.__testvalue__, id=vid, value=12.4, space=s, result=r)
        assert v.id == vid
        assert v.value == 12.4
        assert v.space == s.id
        assert v.result == r.id

        v = b.make(self.__testvalue__, id=vid, value='foo', space=s.id, result=r.id)
        assert v.id == vid
        assert v.value == 'foo'
        assert v.space == s.id
        assert v.result == r.id

        # Test making Results
        r = b.make(self.__testresult__)
        assert hasattr(r, 'id')
        assert r.loss is None
        assert r.results is None
        assert r.tree is None
        assert r.values == []

        rid = str(uuid.uuid4())
        t = self.__testtree__()
        v = self.__testvalue__()

        r = b.make(self.__testresult__, id=rid, loss=0.00154, results={'foo': 'bar'},
                                tree=t, values=[v])
        assert r.id == rid
        assert r.loss == 0.00154
        assert r.results == {'foo': 'bar'}
        assert r.tree == t.id
        assert r.values == [v.id]

        r = b.make(self.__testresult__, tree=t.id, values=[v.id])
        assert r.tree == t.id
        assert r.values == [v.id]

    def test_checkpoint(self):
        pass

    def test_make_forest(self):
        # Test creating a flat forest
        spec = {
            'domain': [1, 2, 3],
            'scaling': 'linear',
            'strategy': 'random'
        }

        b = JSONBackend()
        trees = b.make_forest(spec)
        t = b.get(Tree, trees[0])
        assert len(trees) == 1
        assert len(b.db['trees']) == 1
        assert len(b.db['spaces']) == 1
        spec['tree'] = t.id
        spec['values'] = []
        assert b.db['spaces'][t.spaces[0]] == spec
        assert t.priority == 1
        assert t.complexity == complexity([1, 2, 3])
        assert t.rank == 0
        assert t.results == []

        # Test creating a forest with one tree and two spaces
        spec = OrderedDict({
            'a': {
                'domain': [1, 2, 3],
                'scaling': 'linear',
                'strategy': 'random'
            },
            'b': {
                'domain': [4, 5, 6],
                'scaling': 'linear',
                'strategy': 'random'
            }
        })

        b = JSONBackend()
        trees = b.make_forest(spec, use_priority=False)
        t = b.get(Tree, trees[0])
        assert len(trees) == 1
        assert len(b.db['trees']) == 1
        assert len(b.db['spaces']) == 2
        spec['a']['tree'] = t.id
        spec['a']['values'] = []
        spec['b']['tree'] = t.id
        spec['b']['values'] = []
        assert b.db['spaces'][t.spaces[0]] == spec['a']
        assert b.db['spaces'][t.spaces[1]] == spec['b']
        assert t.priority is None
        assert t.complexity == complexity([1, 2, 3]) + complexity([4, 5, 6])
        assert t.rank == 0
        assert t.results == []

        # Test with exclusive flag
        spec = OrderedDict({
            'exclusive': True,
            'a': {
                'domain': [1, 2, 3],
                'scaling': 'linear',
                'strategy': 'random'
            },
            'b': {
                'domain': [4, 5, 6],
                'scaling': 'linear',
                'strategy': 'random'
            }
        })
        b = JSONBackend()
        trees = b.make_forest(spec, use_complexity=False)
        t1 = b.get(Tree, trees[0])
        t2 = b.get(Tree, trees[1])
        assert len(trees) == 2
        assert len(b.db['trees']) == 2
        assert len(b.db['spaces']) == 2
        spec['a']['tree'] = t1.id
        spec['a']['values'] = []
        spec['b']['tree'] = t2.id
        spec['b']['values'] = []
        assert b.db['spaces'][t1.spaces[0]] == spec['a']
        assert b.db['spaces'][t2.spaces[0]] == spec['b']
        assert t1.priority == 1
        assert t1.complexity is None
        assert t1.rank == 0
        assert t1.results == []
        assert len(t1.spaces) == 1
        assert t2.priority == 1
        assert t2.complexity is None
        assert t2.rank == 1
        assert t2.results == []
        assert len(t2.spaces) == 1

        # Test with optional flag
        spec = OrderedDict({
            'optional': True,
            'a': {
                'domain': [1, 2, 3],
                'scaling': 'linear',
                'strategy': 'random'
            },
            'b': {
                'domain': [4, 5, 6],
                'scaling': 'linear',
                'strategy': 'random'
            }
        })
        b = JSONBackend()
        trees = b.make_forest(spec, use_priority=False, use_complexity=False)
        t1 = b.get(Tree, trees[0])
        t2 = b.get(Tree, trees[1])
        assert len(trees) == 2
        assert len(b.db['trees']) == 2
        assert len(b.db['spaces']) == 2
        spec['a']['tree'] = t1.id
        spec['a']['values'] = []
        spec['b']['tree'] = t1.id
        spec['b']['values'] = []
        assert b.db['spaces'][t1.spaces[0]] == spec['a']
        assert b.db['spaces'][t1.spaces[1]] == spec['b']
        assert t1.priority is None
        assert t1.complexity is None
        assert t1.rank is None
        assert t1.results == []
        assert len(t1.spaces) == 2
        assert t2.priority is None
        assert t2.complexity is None
        assert t2.rank is None
        assert t2.results == []
        assert len(t2.spaces) == 0

        # Test with exclusive and optional flags
        spec = OrderedDict({
            'exclusive': True,
            'optional': True,
            'a': {
                'domain': [1, 2, 3],
                'scaling': 'linear',
                'strategy': 'random'
            },
            'b': {
                'domain': [4, 5, 6],
                'scaling': 'linear',
                'strategy': 'random'
            }
        })
        b = JSONBackend()
        trees = b.make_forest(spec)
        t1 = b.get(Tree, trees[0])
        t2 = b.get(Tree, trees[1])
        t3 = b.get(Tree, trees[2])
        assert len(trees) == 3
        assert len(b.db['trees']) == 3
        assert len(b.db['spaces']) == 2
        spec['a']['tree'] = t1.id
        spec['a']['values'] = []
        spec['b']['tree'] = t2.id
        spec['b']['values'] = []
        assert b.db['spaces'][t1.spaces[0]] == spec['a']
        assert b.db['spaces'][t2.spaces[0]] == spec['b']
        assert t1.priority == 1
        assert t1.complexity == complexity([1, 2, 3])
        assert t1.rank == 0
        assert t1.results == []
        assert len(t1.spaces) == 1
        assert t2.priority == 1
        assert t2.complexity == complexity([4, 5, 6])
        assert t2.rank == 1
        assert t2.results == []
        assert len(t2.spaces) == 1
        assert t3.priority == 1
        assert t3.complexity == 0
        assert t3.rank == 2
        assert t3.results == []
        assert len(t3.spaces) == 0

        # Put the big test here



    def test_generate(self):
        pass

    def test_register_result(self):
        pass

    def test_get_optimal(self):
        pass


class TestTree(TestBaseTree):
    __testtree__ = Tree
    __testspace__ = Space
    __testvalue__ = Value
    __testresult__ = Result

    def test_init(self):
        # Test default initialization
        t = self.__testtree__()
        assert hasattr(t, 'id')
        assert t.priority is None
        assert t.complexity is None
        assert t.rank is None
        assert t.spaces == []
        assert t.results == []

        # Test with initialized values
        t = self.__testtree__(complexity=1, priority=1, rank=1,
                 spaces=['1', '2', '3', '4', '5'],
                 results=['6', '7', '8', '9', '10'])
        assert hasattr(t, 'id')
        assert t.priority == 1
        assert t.complexity == 1
        assert t.rank == 1
        assert t.spaces == ['1', '2', '3', '4', '5']
        assert t.results == ['6', '7', '8', '9', '10']

        # Test with provided id, Space and Result objects passed
        s1 = self.__testspace__()
        r1 = self.__testresult__()
        tid = str(uuid.uuid4())
        t = self.__testtree__(id=tid, complexity=1, priority=1, rank=1, spaces=[s1],
                 results=[r1])
        assert t.id == tid
        assert t.priority == 1
        assert t.complexity == 1
        assert t.rank == 1
        assert t.spaces == [s1.id]
        assert t.results == [r1.id]

    def test_add_space(self):
        t = self.__testtree__()

        # Test adding a Space object
        s1 = self.__testspace__()
        t.add_space(s1)
        assert t.spaces == [s1.id]

        # Test adding an id
        sid = str(uuid.uuid4())
        t.add_space(sid)
        assert t.spaces == [s1.id, sid]

        # Test giving warning when invalid object added
        with pytest.warns(UserWarning):
            t.add_space(309)

        assert t.spaces == [s1.id, sid]

    def test_add_result(self):
        t = self.__testtree__()

        # Test adding a Space object
        r1 = self.__testresult__()
        t.add_result(r1)
        assert t.results == [r1.id]

        # Test adding an id
        rid = str(uuid.uuid4())
        t.add_result(rid)
        assert t.results == [r1.id, rid]

        # Test giving warning when invalid object added
        with pytest.warns(UserWarning):
            t.add_result(309)

        assert t.results == [r1.id, rid]


class TestSpace(TestBaseSpace):
    __testtree__ = Tree
    __testspace__ = Space
    __testvalue__ = Value
    __testresult__ = Result

    def test_init(self):
        # Test the default initialization
        s = self.__testspace__()
        assert hasattr(s, 'id')
        assert s.domain is None
        assert s.strategy == 'random'
        assert s.scaling == 'linear'
        assert s.tree is None
        assert s.values == []

        # Test setting id, constant domain, strategy, scaling, tree, and values
        t = self.__testtree__()
        v = self.__testvalue__()
        sid = str(uuid.uuid4())
        s = self.__testspace__(id=sid, domain=1, strategy='tpe', scaling='ln', tree=t,
                  values=[v])
        assert s.id == sid
        assert s.domain == 1
        assert s.strategy == 'tpe'
        assert s.scaling == 'ln'
        assert s.tree == t.id
        assert s.values == [v.id]

        # Test setting discrete domain, tree by id, and value by id
        s = self.__testspace__(id=sid, domain=[1, 2, 3, 4], tree=t.id, values=[v.id])
        assert s.domain == [1, 2, 3, 4]
        assert s.tree == t.id
        assert s.values == [v.id]

        # Test setting continuous domain from `scipy.stats.rv_continuous`
        dist = scipy.stats.uniform(loc=-7, scale=42)
        s = self.__testspace__(domain=dist)
        assert s.domain is dist

        # Test setting continuous domain from dictionary
        rng = np.random.RandomState().get_state()
        domain = {
            'distribution': 'uniform',
            'args': [],
            'kwargs': {
                'loc': -7,
                'scale': 42,
            },
            'rng': [rng[0], list(rng[1]), rng[2], rng[3], rng[4]]
        }
        s = self.__testspace__(domain=domain)
        assert s.domain.dist.name == 'uniform'
        assert s.domain.args == ()
        assert s.domain.kwds == {'loc': -7, 'scale': 42}
        state = s.domain.random_state.get_state()
        assert state[0] == rng[0]
        assert np.all(state[1] == np.array(rng[1]))
        assert state[2] == rng[2]
        assert state[3] == rng[3]
        assert state[4] == rng[4]

    def test_add_value(self):
        s = self.__testspace__()

        # Test adding a Value object
        v = self.__testvalue__()
        s.add_value(v)
        assert s.values == [v.id]

        # Test adding an id
        vid = str(uuid.uuid4())
        s.add_value(vid)
        assert s.values == [v.id, vid]

        with pytest.warns(UserWarning):
            s.add_value(8456)

        assert s.values == [v.id, vid]


class TestValue(TestBaseValue):
    __testtree__ = Tree
    __testspace__ = Space
    __testvalue__ = Value
    __testresult__ = Result

    def test_init(self):
        # Test default initialization
        v = self.__testvalue__()
        assert hasattr(v, 'id')
        assert v.value is None
        assert v.space is None
        assert v.value is None

        # Test with id, value, Space object, and Result object
        vid = str(uuid.uuid4())
        s = self.__testspace__()
        r = self.__testresult__()

        v = self.__testvalue__(id=vid, value=12.4, space=s, result=r)
        assert v.id == vid
        assert v.value == 12.4
        assert v.space == s.id
        assert v.result == r.id

        # Test with nonnumeric value, space id, and result id
        v = self.__testvalue__(id=vid, value='foo', space=s.id, result=r.id)
        assert v.id == vid
        assert v.value == 'foo'
        assert v.space == s.id
        assert v.result == r.id


class TestResult(TestBaseResult):
    __testtree__ = Tree
    __testspace__ = Space
    __testvalue__ = Value
    __testresult__ = Result

    def test_init(self):
        # Test default initialization
        r = self.__testresult__()
        assert hasattr(r, 'id')
        assert r.loss is None
        assert r.results is None
        assert r.tree is None
        assert r.values == []

        # Test with id, loss, results, Tree object, and Value object
        rid = str(uuid.uuid4())
        t = self.__testtree__()
        v = self.__testvalue__()

        r = self.__testresult__(id=rid, loss=0.00154, results={'foo': 'bar'},
                                tree=t, values=[v])
        assert r.id == rid
        assert r.loss == 0.00154
        assert r.results == {'foo': 'bar'}
        assert r.tree == t.id
        assert r.values == [v.id]

        # Test with Tree id and value id
        r = self.__testresult__(tree=t.id, values=[v.id])
        assert r.tree == t.id
        assert r.values == [v.id]
