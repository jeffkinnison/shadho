import pytest

from shadho.backend.base.db import BaseBackend

from collections import OrderedDict


class TestBaseBackend(object):
    def test_split_spec(self):
        b = BaseBackend()

        # Test a flat search
        spec = {
            'domain': [1, 2, 3],
            'scaling': 'linear',
            'strategy': 'random'
        }

        tree = b.split_spec(spec)
        assert tree == [[spec]]
        assert spec['path'] == ''

        # Test a flat search with multiple spaces
        spec = OrderedDict()
        spec['a'] = {
            'domain': [1, 2, 3],
            'scaling': 'linear',
            'strategy': 'random'
        }

        spec['b'] = {
            'domain': [4, 5, 6],
            'scaling': 'linear',
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
            'scaling': 'linear',
            'strategy': 'random'
        }

        spec['A']['b'] = {
            'domain': 2,
            'scaling': 'linear',
            'strategy': 'random'
        }

        spec['A']['c'] = {
            'domain': 3,
            'scaling': 'linear',
            'strategy': 'random'
        }

        spec['B']['d'] = {
            'domain': 4,
            'scaling': 'linear',
            'strategy': 'random'
        }

        spec['B']['e'] = {
            'domain': 5,
            'scaling': 'linear',
            'strategy': 'random'
        }

        spec['C']['f'] = {
            'domain': 6,
            'scaling': 'linear',
            'strategy': 'random'
        }

        spec['C']['g'] = {
            'domain': 7,
            'scaling': 'linear',
            'strategy': 'random'
        }

        spec['D']['h'] = {
            'domain': 8,
            'scaling': 'linear',
            'strategy': 'random'
        }

        spec['D']['i'] = {
            'domain': 9,
            'scaling': 'linear',
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
