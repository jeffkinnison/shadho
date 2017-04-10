'''
'''

from shadho.spaces import BaseSpace, ConstantSpace, ContinuousSpace, DiscreteSpace
from shadho.spaces import DistributionDoesNotExist
from shadho.strategies import random
from shadho.scales import linear, ln, log10, log2

from nose.tools import assert_equal, assert_is, assert_is_none, raises
from nose.tools import assert_is_instance, assert_less, assert_greater_equal
from nose.tools import assert_list_equal, assert_dict_equal, assert_in

import numpy as np
import scipy.stats


class TestBaseSpace(object):
    '''Test shadho.spaces.BaseSpace.
    '''

    def test_generate(self):
        '''Test that the base space only generates None.
        '''
        sp = BaseSpace()
        assert_is_none(sp.generate(), msg='BaseSpace has non-None value')

    def test_to_spec(self):
        '''Test that the specification of the base space is None.
        '''
        sp = BaseSpace()
        assert_is_none(sp.to_spec(), msg='BaseSpace generates actual spec')

    def test_complexity(self):
        '''Test that the complexity of the base space is 1.
        '''
        sp = BaseSpace()
        assert_equal(sp.complexity(), 1, msg='BaseSpace complexity is not 1')


class TestConstantSpace(object):
    '''Test shadho.spaces.ConstantSpace.
    '''

    @raises(TypeError)
    def test_init(self):
        '''Test that ConstantSpace sets the assigned value.
        '''
        # Test value assignment
        sp = ConstantSpace(5)
        assert_equal(sp.value, 5, msg='ConstantSpace does not set constant')

        # Ensure that a value must be passed (raises a TypeError)
        sp = ConstantSpace()

    def test_generate(self):
        '''Test that the constant space only generates the assigned value.
        '''
        sp = ConstantSpace(5)
        for i in range(1000):
            assert_equal(sp.generate(), 5, msg='ConstantSpace generates incorrect value')

    def test_to_spec(self):
        '''Test that the specification of the constant space is the value.
        '''
        sp = ConstantSpace(5)
        assert_equal(sp.to_spec(), 5, msg='BaseSpace generates actual spec')

    def test_complexity(self):
        '''Test that the complexity of the constant space is 1.
        '''
        sp = ConstantSpace(5)
        assert_equal(sp.complexity(), 1, msg='ConstantSpace complexity is not 1')


class TestContinuousSpace(object):
    '''Test shadho.spaces.ContinuousSpace.
    '''

    @raises(DistributionDoesNotExist)
    def test_init(self):
        '''Test that ContinuousSpace initializes correctly.
        '''
        # Test default value assignment
        sp = ContinuousSpace()
        assert_is(sp.distribution, scipy.stats.uniform, msg='Uniform distro not set by default')
        assert_is(sp.strategy, random, msg='Random Search not set by default')
        assert_is(sp.scale, linear, msg='Linear scale not used by default')
        assert_is_instance(sp.rng, np.random.RandomState, msg='RNG not created')

        # Test probability distribution assignment
        sp = ContinuousSpace(distribution='norm')
        assert_is(sp.distribution, scipy.stats.norm, msg='Normal distro not set')
        assert_is(sp.strategy, random, msg='Random Search not set by default')
        assert_is(sp.scale, linear, msg='Linear scale not used by default')
        assert_is_instance(sp.rng, np.random.RandomState, msg='RNG not created')

        # Test scale assignment
        sp = ContinuousSpace(scaling='log10')
        assert_is(sp.distribution, scipy.stats.uniform, msg='Uniform distro not set by default')
        assert_is(sp.strategy, random, msg='Random Search not set by default')
        assert_is(sp.scale, log10, msg='Log base 10 scale not set')
        assert_is_instance(sp.rng, np.random.RandomState, msg='RNG not created')

        # Test rng assignment
        r = np.random.RandomState(1234)
        sp = ContinuousSpace(rng=r)
        assert_is(sp.distribution, scipy.stats.uniform, msg='Uniform distro not set by default')
        assert_is(sp.strategy, random, msg='Random Search not set by default')
        assert_is(sp.scale, linear, msg='Linear scale not used by default')
        assert_is(sp.rng, r, msg='RNG not created')

        # Test seed assignment
        r = np.random.RandomState(1234)
        sp = ContinuousSpace(seed=1234)
        assert_is(sp.distribution, scipy.stats.uniform, msg='Uniform distro not set by default')
        assert_is(sp.strategy, random, msg='Random Search not set by default')
        assert_is(sp.scale, linear, msg='Linear scale not used by default')

        x = sp.distribution.rvs(random_state=sp.rng, size=1000)
        y = scipy.stats.uniform.rvs(random_state=r, size=1000)
        assert_list_equal(list(x), list(y), msg='Random seed 1234 not set')


        # Ensure a distribution is passed (raises DistributionDoesNotExist)
        sp = ContinuousSpace(distribution='fail')

    def test_generate(self):
        '''Test that the constant space generates from the assigned distribution.
        '''
        sp = ContinuousSpace(seed=1234)
        r = np.random.RandomState(1234)
        x = [sp.generate() for i in range(1000)]
        y = scipy.stats.uniform.rvs(random_state=r, size=1000)
        assert_list_equal(x, list(y), msg='ContinuousSpace generates incorrect values')

        sp = ContinuousSpace(distribution='norm', seed=1234)
        r = np.random.RandomState(1234)
        x = [sp.generate() for i in range(1000)]
        y = scipy.stats.norm.rvs(random_state=r, size=1000)
        assert_list_equal(x, list(y), msg='ContinuousSpace generates incorrect values')

    def test_to_spec(self):
        '''Test that the specification of the constant space is the value.
        '''
        sp = ContinuousSpace()
        spec = {
            'distribution': 'uniform',
            'args': (),
            'kwargs': {},
            'strategy': 'random',
            'scale': 'linear'
        }
        assert_dict_equal(sp.to_spec(), spec, msg='BaseSpace does not generate spec')

    def test_complexity(self):
        '''Test that the complexity of the constant space is 0.
        '''
        sp = ContinuousSpace()
        interval = scipy.stats.uniform.interval(.99)
        distance = 2 + np.linalg.norm(interval[1] - interval[0])
        assert_equal(sp.complexity(), distance, msg='Complexity calculation is wrong')

        sp = ContinuousSpace(loc=2.8, scale=33.56)
        interval = scipy.stats.uniform.interval(.99, loc=2.8, scale=33.56)
        distance = 2 + np.linalg.norm(interval[1] - interval[0])
        assert_equal(sp.complexity(), distance, msg='Complexity calculation is wrong')


class TestDiscreteSpace(object):
    '''Test shadho.spaces.ContinuousSpace.
    '''

    def test_init(self):
        '''Test that DiscreteSpace initializes correctly.
        '''
        # Test default initialization
        sp = DiscreteSpace()
        assert_list_equal(sp.values, [], msg='Default empty list not initialized')
        assert_is(sp.distribution, scipy.stats.randint, msg='Default probability distribution not set')
        assert_is(sp.strategy, random, msg='Default random search not set')
        assert_is(sp.scale, linear, msg='Default linear scaling not set')
        assert_is_instance(sp.rng, np.random.RandomState, msg='Default RNG not created')

        # Test default initialization
        sp = DiscreteSpace(values=[1, 2, 3, 4, 5])
        assert_list_equal(sp.values, [1, 2, 3, 4, 5], msg='Supplied values not set')
        assert_is(sp.distribution, scipy.stats.randint, msg='Default probability distribution not set')
        assert_is(sp.strategy, random, msg='Default random search not set')
        assert_is(sp.scale, linear, msg='Default linear scaling not set')
        assert_is_instance(sp.rng, np.random.RandomState, msg='Default RNG not created')

    def test_generate(self):
        '''Test that the constant space generates from the assigned distribution.
        '''
        sp = DiscreteSpace(values=[1, 2, 3, 4, 5])
        for i in range(1000):
            assert_in(sp.generate(), [1, 2, 3, 4, 5], msg='Values not being generated')

        sp = DiscreteSpace(values=['a', 'b', 'c', 'd', 'e'])
        for i in range(1000):
            assert_in(sp.generate(), ['a', 'b', 'c', 'd', 'e'], msg='Values not being generated')

    def test_to_spec(self):
        '''Test that the specification of the constant space is the value.
        '''
        sp = DiscreteSpace()
        spec = {
            'values': [],
            'strategy': 'random',
            'scale': 'linear'
        }
        assert_dict_equal(sp.to_spec(), spec, msg='BaseSpace does not generate spec')

    def test_complexity(self):
        '''Test the complexity of the discrete space.
        '''
        sp = DiscreteSpace()
        assert_equal(sp.complexity(), 1, msg='Complexity calculation is wrong')

        sp = DiscreteSpace(values=[1, 2, 3, 4, 5])
        assert_equal(sp.complexity(), 1 + (4/5), msg='Complexity calculation is wrong')
