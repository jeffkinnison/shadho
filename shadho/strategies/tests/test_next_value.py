import pytest

from shadho.strategies import next_value

import numpy as np
from scipy.stats import randint, uniform


def test_next_value_random():
    # Test with None and builtin values
    x = next_value(None, 'random')
    assert x is None

    x = next_value(1, 'random')
    assert x == 1
    assert isinstance(x, int)

    x = next_value(1.0, 'random')
    assert x == 1.0
    assert isinstance(x, float)

    x = next_value('foo', 'random')
    assert x == 'foo'
    assert isinstance(x, str)

    x = next_value([1, 2, 3], 'random')
    assert x == [1, 2, 3]
    assert isinstance(x, list)

    x = next_value((1, 'foo'), 'random')
    assert x == (1, 'foo')
    assert isinstance(x, tuple)

    x = next_value({'foo': 1}, 'random')
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
        assert next_value(d1, 'random') == d2.rvs()

    d1 = uniform(loc=7, scale=23987)
    d2 = uniform(loc=7, scale=23987)
    d1.random_state = rng1
    d2.random_state = rng2

    for _ in range(1000):
        assert next_value(d1, 'random') == d2.rvs()


def test_next_value_default():
    # Test with None and builtin values
    with pytest.warns(UserWarning):
        x = next_value(None, 'foo')
        assert x is None

    with pytest.warns(UserWarning):
        x = next_value(1, 'foo')
        assert x == 1
        assert isinstance(x, int)

    with pytest.warns(UserWarning):
        x = next_value(1.0, 'foo')
        assert x == 1.0
        assert isinstance(x, float)

    with pytest.warns(UserWarning):
        x = next_value('foo', 'foo')
        assert x == 'foo'
        assert isinstance(x, str)

    with pytest.warns(UserWarning):
        x = next_value([1, 2, 3], 'foo')
        assert x == [1, 2, 3]
        assert isinstance(x, list)

    with pytest.warns(UserWarning):
        x = next_value((1, 'foo'), 'foo')
        assert x == (1, 'foo')
        assert isinstance(x, tuple)

    with pytest.warns(UserWarning):
        x = next_value({'foo': 1}, 'foo')
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
        with pytest.warns(UserWarning):
            assert next_value(d1, 'foo') == d2.rvs()

    d1 = uniform(loc=7, scale=23987)
    d2 = uniform(loc=7, scale=23987)
    d1.random_state = rng1
    d2.random_state = rng2

    for _ in range(1000):
        with pytest.warns(UserWarning):
            assert next_value(d1, 'foo') == d2.rvs()
