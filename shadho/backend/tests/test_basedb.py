import pytest

from shadho.backend.basedb import BaseBackend, BaseTree, BaseSpace, BaseValue
from shadho.backend.basedb import BaseResult

from collections import OrderedDict

import numpy as np
import scipy.stats


class TestBaseBackend(object):
    def test_split_spec(self):
        b = BaseBackend()

        # Test a flat search
        spec = {
            'domain': [1, 2, 3],
            'scale': 'linear',
            'strategy': 'random'
        }

        tree = b.split_spec(spec)
        assert tree == [[spec]]
        assert spec['path'] == ''

        # Test a flat search with multiple spaces
        spec = OrderedDict()
        spec['a'] = {
            'domain': [1, 2, 3],
            'scale': 'linear',
            'strategy': 'random'
        }

        spec['b'] = {
            'domain': [4, 5, 6],
            'scale': 'linear',
            'strategy': 'random'
        }

        tree = b.split_spec(spec)
        assert tree == [[spec['a'], spec['b']]]
        assert spec['a']['path'] == 'a'
        assert spec['b']['path'] == 'b'

        # Test exclusive flag
        spec['exclusive'] = True
        tree = b.split_spec(spec)

        assert tree == [[spec['a']], [spec['b']]]
        assert spec['a']['path'] == 'a'
        assert spec['b']['path'] == 'b'
        del spec['exclusive']

        # Test optional flag
        spec['optional'] = True

        tree = b.split_spec(spec)
        assert tree == [[spec['a'], spec['b']], []]
        assert spec['a']['path'] == 'a'
        assert spec['b']['path'] == 'b'

        # Test both flags
        spec['exclusive'] = True
        tree = b.split_spec(spec)

        assert tree == [[spec['a']], [spec['b']], []]
        assert spec['a']['path'] == 'a'
        assert spec['b']['path'] == 'b'
        del spec['exclusive']
        del spec['optional']

        # Complex, multi-level test
        # The tree will look like
        #              root
        #     /       /    \      \
        #    A       B      C      D
        #  / | \    / \    / \    / \
        # a  b  c  d   e  f   g  h   i
        spec = OrderedDict()
        spec['A'] = OrderedDict()
        spec['B'] = OrderedDict()
        spec['C'] = OrderedDict()
        spec['D'] = OrderedDict()

        spec['B']['exclusive'] = True
        spec['C']['optional'] = True
        spec['D']['exclusive'] = True
        spec['D']['optional'] = True

        spec['A']['a'] = {
            'domain': 1,
            'scale': 'linear',
            'strategy': 'random'
        }

        spec['A']['b'] = {
            'domain': 2,
            'scale': 'linear',
            'strategy': 'random'
        }

        spec['A']['c'] = {
            'domain': 3,
            'scale': 'linear',
            'strategy': 'random'
        }

        spec['B']['d'] = {
            'domain': 4,
            'scale': 'linear',
            'strategy': 'random'
        }

        spec['B']['e'] = {
            'domain': 5,
            'scale': 'linear',
            'strategy': 'random'
        }

        spec['C']['f'] = {
            'domain': 6,
            'scale': 'linear',
            'strategy': 'random'
        }

        spec['C']['g'] = {
            'domain': 7,
            'scale': 'linear',
            'strategy': 'random'
        }

        spec['D']['h'] = {
            'domain': 8,
            'scale': 'linear',
            'strategy': 'random'
        }

        spec['D']['i'] = {
            'domain': 9,
            'scale': 'linear',
            'strategy': 'random'
        }

        result = [
            [spec['A']['a'],
             spec['A']['b'],
             spec['A']['c'],
             spec['B']['d'],
             spec['C']['f'],
             spec['C']['g'],
             spec['D']['h']],

            [spec['A']['a'],
             spec['A']['b'],
             spec['A']['c'],
             spec['B']['d'],
             spec['C']['f'],
             spec['C']['g'],
             spec['D']['i']],

            [spec['A']['a'],
             spec['A']['b'],
             spec['A']['c'],
             spec['B']['d'],
             spec['C']['f'],
             spec['C']['g']],

            [spec['A']['a'],
             spec['A']['b'],
             spec['A']['c'],
             spec['B']['d'],
             spec['D']['h']],

            [spec['A']['a'],
             spec['A']['b'],
             spec['A']['c'],
             spec['B']['d'],
             spec['D']['i']],

            [spec['A']['a'],
             spec['A']['b'],
             spec['A']['c'],
             spec['B']['d']],

            [spec['A']['a'],
             spec['A']['b'],
             spec['A']['c'],
             spec['B']['e'],
             spec['C']['f'],
             spec['C']['g'],
             spec['D']['h']],

            [spec['A']['a'],
             spec['A']['b'],
             spec['A']['c'],
             spec['B']['e'],
             spec['C']['f'],
             spec['C']['g'],
             spec['D']['i']],

            [spec['A']['a'],
             spec['A']['b'],
             spec['A']['c'],
             spec['B']['e'],
             spec['C']['f'],
             spec['C']['g']],

            [spec['A']['a'],
             spec['A']['b'],
             spec['A']['c'],
             spec['B']['e'],
             spec['D']['h']],

            [spec['A']['a'],
             spec['A']['b'],
             spec['A']['c'],
             spec['B']['e'],
             spec['D']['i']],

            [spec['A']['a'],
             spec['A']['b'],
             spec['A']['c'],
             spec['B']['e']]
            ]

        tree = b.split_spec(spec)

        assert tree == result
        assert spec['A']['a']['path'] == 'A/a'
        assert spec['A']['b']['path'] == 'A/b'
        assert spec['A']['c']['path'] == 'A/c'
        assert spec['B']['d']['path'] == 'B/d'
        assert spec['B']['e']['path'] == 'B/e'
        assert spec['C']['f']['path'] == 'C/f'
        assert spec['C']['g']['path'] == 'C/g'
        assert spec['D']['h']['path'] == 'D/h'
        assert spec['D']['i']['path'] == 'D/i'

    def test_new_tree(self):
        # Test defaults
        b = BaseBackend()
        t = b.new_tree()

        assert isinstance(t, BaseTree)

        with pytest.raises(TypeError):
            t = b.new_tree('a')

        with pytest.raises(TypeError):
            t = b.new_tree(k='a')

        with pytest.raises(TypeError):
            t = b.new_tree('a', k='a')

    def test_new_space(self):
        # Test defaults
        b = BaseBackend()
        s = b.new_space()

        assert isinstance(s, BaseSpace)

        with pytest.raises(TypeError):
            s = b.new_space('a')

        with pytest.raises(TypeError):
            s = b.new_space(k='a')

        with pytest.raises(TypeError):
            s = b.new_space('a', k='a')

    def test_new_value(self):
        # Test defaults
        b = BaseBackend()
        v = b.new_value()

        assert isinstance(v, BaseValue)

        with pytest.raises(TypeError):
            v = b.new_value('a')

        with pytest.raises(TypeError):
            v = b.new_value(k='a')

        with pytest.raises(TypeError):
            v = b.new_value('a', k='a')

    def test_new_result(self):
        # Test defaults
        b = BaseBackend()
        r = b.new_result()

        assert isinstance(r, BaseResult)

        with pytest.raises(TypeError):
            r = b.new_result('a')

        with pytest.raises(TypeError):
            r = b.new_result(k='a')

        with pytest.raises(TypeError):
            r = b.new_result('a', k='a')


class TestBaseTree(object):
    def test_generate(self):
        pass

    def test_calculate_priority(self):
        pass

    def test_calculate_complexity(self):
        pass

    def test_optimal_parameters(self):
        pass


class TestBaseSpace(object):
    def test_complexity(self):
        s = BaseSpace()

        # Test None as domain
        s.domain = None
        assert s.complexity == 1

        # Test constant scalar values as domain
        s.domain = 5
        assert s.complexity == 1

        s.domain = 5.0
        assert s.complexity == 1

        s.domain = 'foo'
        assert s.complexity == 1

        # Test list as domain
        s.domain = []
        assert s.complexity == 1

        s.domain = [1, 2, 3, 4]
        assert s.complexity == 1.75

        s.domain = [0 for _ in range(1000)]
        assert s.complexity == 1.999

        # Test continuous random variate as domain
        rs1 = np.random.RandomState(1234)
        rs2 = np.random.RandomState(1234)

        s.domain = scipy.stats.uniform(loc=-7, scale=1000)
        d2 = scipy.stats.uniform(loc=-7, scale=1000)

        s.domain.random_state = rs1
        d2.random_state = rs2

        a, b = d2.interval(0.9999)

        assert s.complexity == 2 + np.linalg.norm(b - a)

    def test_get_label(self):
        s = BaseSpace()

        # Test with list domain
        s.domain = []
        assert s.get_label('foo') == -1

        s.domain = ['foo', 'bar', 'baz']
        assert s.get_label('foo') == 0
        assert s.get_label('meep') == -1

        # Test with non-list domains
        # Should return the value unaltered
        s.domain = 5.0

        assert s.get_label(1) == 1
        assert s.get_label(1.7) == 1.7
        assert s.get_label('foo') == 'foo'
        assert s.get_label([93475]) == [93475]

    def test_generate(self):
        s = BaseSpace()
        s.strategy = 'random'
        s.scaling = 'linear'

        # Test constant domains
        s.domain = None
        assert s.generate() is None

        s.domain = 1
        assert s.generate() == 1

        s.domain = 5.7
        assert s.generate() == 5.7

        s.domain = 'foo'
        assert s.generate() == 'foo'

        # Test discrete domain
        s.domain = [1, 5.7, 'foo']

        for _ in range(1000):
            assert s.generate() in s.domain


class TestBaseValue(object):
    def test_to_numeric(self):
        pass


class TestBaseResult(object):
    def test_to_feature_vector(self):
        pass
