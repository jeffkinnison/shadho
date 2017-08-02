import pytest

from shadho.backend.jsondb import JSONBackend, Tree, Space, Value, Result
from shadho.backend.jsondb import InvalidTableError, InvalidObjectClassError
from shadho.backend.jsondb import InvalidObjectError

from test_basedb import TestBaseBackend, TestBaseTree, TestBaseSpace
from test_basedb import TestBaseValue, TestBaseResult

import uuid

import numpy as np
import scipy.stats


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
            'rng': [rng[0], list(rng[1]), *rng[2:]]
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


class TestResult(TestBaseResult):
    __testtree__ = Tree
    __testspace__ = Space
    __testvalue__ = Value
    __testresult__ = Result
