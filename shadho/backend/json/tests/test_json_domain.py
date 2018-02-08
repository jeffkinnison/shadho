import pytest

from shadho.backend.json.domain import Domain
from shadho.backend.json.model import Model
from shadho.backend.json.value import Value
from shadho.backend.utils import InvalidObjectError
from shadho.backend.base.tests.test_base_domain import TestBaseDomain

import uuid

import numpy as np
import scipy.stats


class TestJsonDomain(TestBaseDomain):
    """Unit tests for the JSON backend Domain class"""

    __model_class__ = Model
    __domain_class__ = Domain
    __value_class__ = Value

    def test_init(self):
        # Test the default initialization
        d = self.__domain_class__()
        assert hasattr(d, 'id')
        assert d.id is not None
        assert d.domain is None
        assert d.strategy == 'random'
        assert d.scaling == 'linear'
        assert d.model is None
        assert d.values == []
        assert d.exhaustive is False
        assert d.exhaustive_idx is None

        # Test setting id, constant domain, strategy, scaling, model, and values
        m = self.__model_class__()
        v = self.__value_class__()
        did = str(uuid.uuid4())
        d = self.__domain_class__(id=did, domain=1, strategy='tpe', scaling='ln', model=m,
                  values=[v])
        assert d.id == did
        assert d.domain == 1
        assert d.strategy == 'tpe'
        assert d.scaling == 'ln'
        assert d.model == m.id
        assert d.values == [v.id]
        assert d.exhaustive is False
        assert d.exhaustive_idx is None

        # Test setting discrete domain, model by id, and value by id
        d = self.__domain_class__(id=did, domain=[1, 2, 3, 4], model=m.id, values=[v.id])
        assert d.domain == [1, 2, 3, 4]
        assert d.model == m.id
        assert d.values == [v.id]
        assert d.exhaustive is False
        assert d.exhaustive_idx is None

        # Test setting a discrete domain with exhaustive search
        d = self.__domain_class__(domain=[1, 2, 3, 4], exhaustive=True)
        assert d.domain == [1, 2, 3, 4]
        assert d.exhaustive
        assert d.exhaustive_idx == 0

        # Test setting continuous domain from `scipy.stats.rv_continuous`
        dist = scipy.stats.uniform(loc=-7, scale=42)
        d = self.__domain_class__(domain=dist)
        assert d.domain is dist

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
        d = self.__domain_class__(domain=domain)
        assert d.domain.dist.name == 'uniform'
        assert d.domain.args == ()
        assert d.domain.kwds == {'loc': -7, 'scale': 42}
        state = d.domain.random_state.get_state()
        assert state[0] == rng[0]
        assert np.all(state[1] == np.array(rng[1]))
        assert state[2] == rng[2]
        assert state[3] == rng[3]
        assert state[4] == rng[4]

    def test_add_value(self):
        d = self.__domain_class__()

        # Test adding a Value object
        v = self.__value_class__()
        d.add_value(v)
        assert d.values == [v.id]

        # Test adding an id
        vid = str(uuid.uuid4())
        d.add_value(vid)
        assert d.values == [v.id, vid]

        with pytest.raises(InvalidObjectError):
            d.add_value((1, 2, 3))

        assert d.values == [v.id, vid]
