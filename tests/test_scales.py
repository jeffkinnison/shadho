from shadho.scales import get_scale, linear, ln, log10, log2

import numpy as np
import scipy.stats

from nose.tools import assert_equal, assert_is, assert_is_instance
from nose.tools import assert_list_equal, raises


class TestScales(object):
    def test_get_scale(self):
        x = get_scale('ln')
        assert_is(x, ln, msg='Incorrect scaling function returned')

        x = get_scale('log10')
        assert_is(x, log10, msg='Incorrect scaling function returned')

        x = get_scale('log2')
        assert_is(x, log2, msg='Incorrect scaling function returned')

        x = get_scale('linear')
        assert_is(x, linear, msg='Incorrect scaling function returned')

        x = get_scale('meep')
        assert_is(x, linear, msg='Default scaling function not returned')

    def test_linear(self):
        # Test on float value
        x = linear(5.0)
        assert_equal(x, 5.0, msg='Incorrect value returned')
        assert_is_instance(x, float, msg='linear cast type from float')

        # Test on int value
        x = linear(5)
        assert_equal(x, 5, msg='Incorrect value returned')
        assert_is_instance(x, int, msg='linear cast type from int')

        # Test on float 0
        x = linear(0.0)
        assert_equal(x, 0.0, msg='Incorrect value returned')
        assert_is_instance(x, float, msg='linear cast type from float')

        # Test on int 0
        x = linear(0)
        assert_equal(x, 0, msg='Incorrect value returned')
        assert_is_instance(x, int, msg='linear cast type from float')

        # Test on a bunch of values
        x = list(scipy.stats.randint.rvs(-1000000, 1000000, size=1000))
        y = [linear(z) for z in x]
        assert_list_equal(y, x, msg='Linear scaling altered values')

        # Test on non-numeric value
        x = linear('a')
        assert_equal(x, 'a', msg='String input altered')
        assert_is_instance(x, str, msg='String input cast from string')

    @raises(TypeError)
    def test_ln(self):
        # Test on float value
        x = ln(5.0)
        assert_equal(x, 148.4131591025766, msg='Incorrect value returned')
        assert_is_instance(x, float, msg='ln cast type from float')

        # Test on int value
        x = ln(5)
        assert_equal(x, 148.4131591025766, msg='Incorrect value returned')
        assert_is_instance(x, float, msg='ln did not cast type to float')

        # Test on float 0
        x = ln(0.0)
        assert_equal(x, 1.0, msg='Incorrect value returned')
        assert_is_instance(x, float, msg='ln cast type from float')

        # Test on int 0
        x = ln(0)
        assert_equal(x, 1.0, msg='Incorrect value returned')
        assert_is_instance(x, float, msg='ln did not cast type to float')

        # Test on a bunch of values
        x = list(scipy.stats.randint.rvs(-10, 10, size=1000))
        y = [ln(z) for z in x]
        x = [np.exp(z) for z in x]
        assert_list_equal(y, x, msg='Log scaling altered values')

        # Non-numeric values should raise a TypeError
        x = ln('a')

    @raises(TypeError)
    def test_log10(self):
        # Test on float value
        x = log10(5.0)
        assert_equal(x, 100000, msg='Incorrect value returned')
        assert_is_instance(x, float, msg='log10 cast type from float')

        # Test on int value
        x = log10(5)
        assert_equal(x, 100000, msg='Incorrect value returned')
        assert_is_instance(x, int, msg='log10 cast type from int')

        # Test on float 0
        x = log10(0.0)
        assert_equal(x, 1.0, msg='Incorrect value returned')
        assert_is_instance(x, float, msg='log10 cast type from float')

        # Test on int 0
        x = log10(0)
        assert_equal(x, 1, msg='Incorrect value returned')
        assert_is_instance(x, int, msg='log10 cast type from int')

        # Test on a bunch of values
        x = list(scipy.stats.randint.rvs(-10, 10, size=1000))
        y = [log10(z) for z in x]
        x = [np.power(10.0, z) for z in x]
        assert_list_equal(y, x, msg='Log scaling altered values')

        # Non-numeric values should raise a TypeError
        x = log10('a')

    @raises(TypeError)
    def test_log2(self):
        # Test on float value
        x = log2(5.0)
        assert_equal(x, 32.0, msg='Incorrect value returned')
        assert_is_instance(x, float, msg='log2 cast type from float')

        # Test on int value
        x = log2(5)
        assert_equal(x, 32, msg='Incorrect value returned')
        assert_is_instance(x, int, msg='log2 cast type from int')

        # Test on float 0
        x = log2(0.0)
        assert_equal(x, 1.0, msg='Incorrect value returned')
        assert_is_instance(x, float, msg='log2 cast type from float')

        # Test on int 0
        x = log2(0)
        assert_equal(x, 1, msg='Incorrect value returned')
        assert_is_instance(x, int, msg='log2 cast type from int')

        # Test on a bunch of values
        x = list(scipy.stats.randint.rvs(-10, 10, size=1000))
        y = [log2(z) for z in x]
        x = [np.exp2(z) for z in x]
        assert_list_equal(y, x, msg='Log scaling altered values')

        # Non-numeric values should raise a TypeError
        x = log2('a')
