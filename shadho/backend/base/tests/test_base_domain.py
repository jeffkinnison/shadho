import pytest

from shadho.backend.base.domain import BaseDomain
from shadho.backend.base.value import BaseValue

import numpy as np
import scipy.stats


class TestBaseDomain(object):
    """Unit tests for the BaseDomain class"""

    __domain_class__ = BaseDomain
    __value_class__ = BaseValue

    def test_tablename(self):
        """Ensure that BaseDomain instances have the correct table name."""
        assert self.__domain_class__.__tablename__ == 'domains'

    def test_add_value(self):
        """Ensure that BaseDomain does not implement an add_value method."""
        d = self.__domain_class__()

        with pytest.raises(NotImplementedError):
            d.add_value(self.__value_class__)

    def test_complexity(self):
        d = self.__domain_class__()
        d.exhaustive = False

        # Test None as domain
        d.domain = None
        assert d.complexity == 1

        # Test constant scalar values as domain
        d.domain = 5
        assert d.complexity == 1

        d.domain = 5.0
        assert d.complexity == 1

        d.domain = 'foo'
        assert d.complexity == 1

        # Test list as domain
        d.domain = []
        assert d.complexity == 1

        d.domain = [1, 2, 3, 4]
        assert d.complexity == 1.75

        d.domain = [0 for _ in range(1000)]
        assert d.complexity == 1.999

        # Test continuous random variate as domain
        rs1 = np.random.RandomState(1234)
        rs2 = np.random.RandomState(1234)

        d.domain = scipy.stats.uniform(loc=-7, scale=1000)
        d2 = scipy.stats.uniform(loc=-7, scale=1000)

        d.domain.random_state = rs1
        d2.random_state = rs2

        a, b = d2.interval(0.9999)

        assert d.complexity == 2 + np.linalg.norm(b - a)

    def test_get_label(self):
        d = self.__domain_class__()
        d.exhaustive = False

        # Test with list domain
        d.domain = []
        assert d.get_label('foo') == -1

        d.domain = ['foo', 'bar', 'baz']
        assert d.get_label('foo') == 0
        assert d.get_label('bar') == 1
        assert d.get_label('baz') == 2
        assert d.get_label('meep') == -1

        # Test with constant domains
        # Should return 0 if equal to the domain, else -1
        d.domain = 5.0
        assert d.get_label(5.0) == 0
        assert d.get_label(1) == -1
        assert d.get_label(1.7) == -1
        assert d.get_label('foo') == -1
        assert d.get_label(None) == -1

        d.domain = 1
        assert d.get_label(5.0) == -1
        assert d.get_label(1) == 0
        assert d.get_label(1.7) == -1
        assert d.get_label('foo') == -1
        assert d.get_label(None) == -1

        d.domain = 1.7
        assert d.get_label(5.0) == -1
        assert d.get_label(1) == -1
        assert d.get_label(1.7) == 0
        assert d.get_label('foo') == -1
        assert d.get_label(None) == -1

        d.domain = 'foo'
        assert d.get_label(5.0) == -1
        assert d.get_label(1) == -1
        assert d.get_label(1.7) == -1
        assert d.get_label('foo') == 0
        assert d.get_label(None) == -1

        d.domain = None
        assert d.get_label(5.0) == -1
        assert d.get_label(1) == -1
        assert d.get_label(1.7) == -1
        assert d.get_label('foo') == -1
        assert d.get_label(None) == 0

        # Test continuous domain
        # Should return the value unaltered
        d.domain = scipy.stats.uniform(loc=-7, scale=42)
        assert d.get_label(23.9) == 23.9
        assert d.get_label(3.05) == 3.05
        assert d.get_label(-84356) == -84356

    def test_generate(self):
        d = self.__domain_class__()
        d.strategy = 'random'
        d.scaling = 'linear'

        # Test constant domains
        d.domain = None
        assert d.generate() is None

        d.domain = 1
        assert d.generate() == 1

        d.domain = 5.7
        assert d.generate() == 5.7

        d.domain = 'foo'
        assert d.generate() == 'foo'

        # Test discrete domain
        d.domain = []
        assert d.generate() == []

        d.domain = [1, 5.7, 'foo']
        for _ in range(1000):
            assert d.generate() in d.domain

        # Test continuous domain
        d.domain = scipy.stats.uniform(loc=-7, scale=42)
        d2 = scipy.stats.uniform(loc=-7, scale=42)

        d.domain.random_state = np.random.RandomState(1234)
        d2.random_state = np.random.RandomState(1234)

        for _ in range(1000):
            assert d.generate() == d2.rvs()
