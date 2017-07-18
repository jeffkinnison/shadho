import pytest

from shadho.strategies import random_search

import numpy as np
from scipy.stats import randint, uniform


def test_random_search():
    # Test with None and builtin values
    x = random_search(None)
    assert x is None

    x = random_search(1)
    assert x == 1
    assert isinstance(x, int)

    x = random_search(1.0)
    assert x == 1.0
    assert isinstance(x, float)

    x = random_search('foo')
    assert x == 'foo'
    assert isinstance(x, str)

    x = random_search([1, 2, 3])
    assert x == [1, 2, 3]
    assert isinstance(x, list)

    x = random_search((1, 'foo'))
    assert x == (1, 'foo')
    assert isinstance(x, tuple)

    x = random_search({'foo': 1})
    assert x == {'foo': 1}
    assert isinstance(x, dict)

    # Test with scipy.stats random variates
    rng1 = np.random.RandomState(1234)
    rng2 = np.random.RandomState(1234)

    d1 = randint(low=7, high=23987)
    d2 = randint(low=7, high=23987)
    d1.random_state = rng1
    d2.random_state = rng2

    for _ in range(1000):
        assert random_search(d1) == d2.rvs()

    d1 = uniform(loc=7, scale=23987)
    d2 = uniform(loc=7, scale=23987)
    d1.random_state = rng1
    d2.random_state = rng2

    for _ in range(1000):
        assert random_search(d1) == d2.rvs()
