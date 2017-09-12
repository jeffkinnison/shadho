import pytest

from shadho.scaling import scale_value, linear, ln, log_10, log_2

import numpy as np


def test_scale_value():
    # Test linear
    x = scale_value(1, 'linear')
    v = 1
    assert x == v
    assert isinstance(x, int)

    # Test linear
    x = scale_value(1, 'ln')
    v = np.exp(1)
    assert x == v
    assert isinstance(x, float)

    # Test linear
    x = scale_value(1, 'log_10')
    v = np.power(10, 1)
    assert x == v
    assert isinstance(x, int)

    # Test linear
    x = scale_value(1, 'log_2')
    v = np.exp2(1)
    assert x == v
    assert isinstance(x, int)

    # Test providing a custom function
    x = scale_value(1, lambda y: np.sqrt(y * 7))
    v = np.sqrt(1 * 7)
    assert x == v

    # Test providing a custom callable object
    class DummyScale(object):
        def __call__(self, x):
            return np.sqrt(x * 7)

    x = scale_value(1, DummyScale())
    v = np.sqrt(1 * 7)
    assert x == v

    # Check that linear is used whenevre an invalid scale is provided
    with pytest.warns(UserWarning):
        x = scale_value(1, 'foo')
        assert x == 1
        assert isinstance(x, int)


def test_linear():
    # Test defaults
    vals = np.random.randint(-1e9, high=1e9, size=1000)
    for v in vals:
        x = linear(v)
        assert x == v, "Value {} changed to {}".format(v, x)

    # Test with a coefficient
    coeff = np.random.rand(*vals.shape)
    for i in range(len(vals)):
        x = linear(vals[i].astype(np.float64), coeff=coeff[i])
        v = vals[i] * coeff[i]
        assert x == v, "{} is not {}".format(x, v)

    # Test with exponent
    exp = np.random.randint(-10, 10, size=vals.shape)
    for i in range(len(vals)):
        x = linear(vals[i].astype(np.float64), degree=exp[i])
        v = np.power(vals[i].astype(np.float64),  exp[i])
        assert x == v, "{} is not {}".format(x, v)

    # Test with both
    for i in range(len(vals)):
        x = linear(vals[i].astype(np.float64), coeff=coeff[i], degree=exp[i])
        v = coeff[i] * np.power(vals[i].astype(np.float64),  exp[i])
        assert x == v, "{} is not {}".format(x, v)

    # Test that type is preserved
    x = linear(1)
    assert x == 1
    assert isinstance(x, int)

    x = linear(1.0)
    assert x == 1.0
    assert isinstance(x, float)

    x = linear('1')
    assert x == '1'
    assert isinstance(x, str)

    x = linear([1])
    assert x == [1]
    assert isinstance(x, list)

    x = linear({1})
    assert x == {1}
    assert isinstance(x, set)

    x = linear({1: 1})
    assert x == {1: 1}
    assert isinstance(x, dict)

    x = linear(None)
    assert x is None


def test_ln():
    # Test defaults
    vals = np.random.randn(1000)
    for i in range(len(vals)):
        x = ln(vals[i])
        v = np.exp(vals[i])
        assert x == v, "Value {} changed to {}".format(v, x)

    # Test that the resultant type is as described in the documentation
    x = ln(0)
    assert x == 1
    assert isinstance(x, float)

    x = ln(0.0)
    assert x == 1.0
    assert isinstance(x, float)

    x = ln('1')
    assert x == '1'
    assert isinstance(x, str)

    x = ln([1])
    assert x == [1]
    assert isinstance(x, list)

    x = ln({1})
    assert x == {1}
    assert isinstance(x, set)

    x = ln({1: 1})
    assert x == {1: 1}
    assert isinstance(x, dict)

    x = ln(None)
    assert x is None


def test_log_10():
    # Test defaults
    vals = np.random.randn(1000)
    for i in range(len(vals)):
        x = log_10(vals[i])
        v = np.power(10, vals[i])
        assert x == v, "Value {} changed to {}".format(v, x)

    # Test that the resultant type is as described in the documentation
    x = log_10(0)
    assert x == 1
    assert isinstance(x, int)

    x = log_10(0.0)
    assert x == 1.0
    assert isinstance(x, float)

    x = log_10('1')
    assert x == '1'
    assert isinstance(x, str)

    x = log_10([1])
    assert x == [1]
    assert isinstance(x, list)

    x = log_10({1})
    assert x == {1}
    assert isinstance(x, set)

    x = log_10({1: 1})
    assert x == {1: 1}
    assert isinstance(x, dict)

    x = log_10(None)
    assert x is None


def test_log_2():
    # Test defaults
    vals = np.random.randn(1000)
    for i in range(len(vals)):
        x = log_2(vals[i])
        v = np.exp2(vals[i])
        assert x == v, "Value {} changed to {}".format(v, x)

    # Test that the resultant type is as described in the documentation
    x = log_2(0)
    assert x == 1
    assert isinstance(x, int)

    x = log_2(0.0)
    assert x == 1.0
    assert isinstance(x, float)

    x = log_2('1')
    assert x == '1'
    assert isinstance(x, str)

    x = log_2([1])
    assert x == [1]
    assert isinstance(x, list)

    x = log_2({1})
    assert x == {1}
    assert isinstance(x, set)

    x = log_2({1: 1})
    assert x == {1: 1}
    assert isinstance(x, dict)

    x = log_2(None)
    assert x is None
