from shadho.tree import SearchTree, SearchTreeNode, SearchTreeLeaf
from shadho.spaces import BaseSpace, ConstantSpace, ContinuousSpace, DiscreteSpace

import numpy as np
import scipy.stats

from nose.tools import assert_equal, assert_is_none, assert_is_instance
from nose.tools import assert_true, assert_false, assert_is, assert_in
from nose.tools import assert_list_equal, assert_dict_equal


class TestSearchTreeLeaf(object):
    def test_init(self):
        # Test the default initialization
        lf = SearchTreeLeaf('test')
        assert_equal(lf.name, 'test', msg='Supplied name not set')
        assert_is_instance(lf.value, BaseSpace, msg='Default value not set')
        assert_false(lf.optional, msg='Optional flag not false by default')

        # Test supplying a value
        val = ContinuousSpace(distribution='norm', loc=2.7, scale=0.33, scaling='ln')
        lf = SearchTreeLeaf('test3', value=val)
        assert_equal(lf.name, 'test3', msg='Supplied name not set')
        assert_is(lf.value, val, msg='Supplied space not set')
        assert_false(lf.optional, msg='Optional flag not false by default')

        # Test setting optional flag
        lf = SearchTreeLeaf('test4', optional=True)
        assert_equal(lf.name, 'test4', msg='Supplied name not set')
        assert_is_instance(lf.value, BaseSpace, msg='Default value not set')
        assert_true(lf.optional, msg='Optional flag not set')

    def test_generate(self):
        # Test the default initialization
        lf = SearchTreeLeaf('test')
        assert_is_none(lf.generate(), msg='Default generated value is not None')

        # Test generating constant value
        val = ConstantSpace(1)
        lf = SearchTreeLeaf('test2', value=val)
        for i in range(1000):
            assert_equal(lf.generate(), 1, msg='Non-constant value generated')

        # Test generating discrete value
        val = DiscreteSpace(values=[1, 2, 3, 4, 5])
        lf = SearchTreeLeaf('test3', value=val)
        for i in range(1000):
            assert_in(lf.generate(), [1, 2, 3, 4, 5], msg='Incorrect value generated')

        # Test generating values from continuous space
        val = ContinuousSpace(seed=1234)
        lf = SearchTreeLeaf('test2', value=val)
        x = list(scipy.stats.uniform.rvs(size=1000, random_state=np.random.RandomState(1234)))
        y = [lf.generate() for i in range(1000)]
        assert_list_equal(x, y)

    def test_split_spaces(self):
        lf = SearchTreeLeaf('test')
        assert_equal(lf.split_spaces()[0], lf, msg='Did not split correctly')

        lf = SearchTreeLeaf('test', optional=True)
        x = lf.split_spaces()
        assert_equal(x[0], lf, msg='Did not split correctly')
        assert_is_none(x[1], msg='Optional space not generated')

    def test_complexity(self):
        lf = SearchTreeLeaf('test')
        assert_equal(lf.complexity(), 1, msg='Complexity not returned')

        val = ConstantSpace(1)
        lf = SearchTreeLeaf('test', value=val)
        assert_equal(lf.complexity(), 1, msg='Complexity not returned')

        val = DiscreteSpace(values=[1, 2, 3, 4, 5])
        lf = SearchTreeLeaf('test', value=val)
        assert_equal(lf.complexity(), 1.8, msg='Complexity not returned')

        val = ContinuousSpace()
        lf = SearchTreeLeaf('test', value=val)
        lo, hi = scipy.stats.uniform.interval(.99)
        dist = 2 + np.linalg.norm(hi - lo)
        assert_equal(lf.complexity(), dist, msg='Complexity not returned')


class TestSearchTreeNode(object):
    def test_init(self):
        # test default initialization
        nd = SearchTreeNode('test')
        assert_equal(nd.name, 'test', msg='Passed name not set')
        assert_list_equal(nd.children, [], msg='Default child list is not empty')
        assert_false(nd.exclusive, msg='Exclusive flag not set to false')
        assert_false(nd.optional, msg='Optional flag not set to false')

        # Test initialization with children
        kids = [SearchTreeLeaf('const', value=ConstantSpace(1)),
                SearchTreeLeaf('disc', value=DiscreteSpace(values=[1, 2, 3, 4, 5])),
                SearchTreeLeaf('cont', value=ContinuousSpace())]

        nd = SearchTreeNode('test', children=kids)
        assert_equal(nd.name, 'test', msg='Passed name not set')
        assert_list_equal(nd.children, kids, msg='Default child list is not empty')
        lo, hi = scipy.stats.uniform.interval(.99)
        dist = 2 + np.linalg.norm(hi - lo)
        total = 1 + 1.8 + dist
        assert_equal(nd._complexity, total, msg='Complexity calculated incorrectly')
        assert_false(nd.exclusive, msg='Exclusive flag not set to false')
        assert_false(nd.optional, msg='Optional flag not set to false')

        # Test setting exclusive flag
        nd = SearchTreeNode('test', exclusive=True)
        assert_equal(nd.name, 'test', msg='Passed name not set')
        assert_list_equal(nd.children, [], msg='Default child list is not empty')
        assert_true(nd.exclusive, msg='Exclusive flag not set to true')
        assert_false(nd.optional, msg='Optional flag not set to false')

        # Test setting optional flag
        nd = SearchTreeNode('test', optional=True)
        assert_equal(nd.name, 'test', msg='Passed name not set')
        assert_list_equal(nd.children, [], msg='Default child list is not empty')
        assert_false(nd.exclusive, msg='Exclusive flag not set to false')
        assert_true(nd.optional, msg='Optional flag not set to true')

    def test_split_spaces(self):
        # Test the default case of splitting an empty node
        nd = SearchTreeNode('test')
        x = nd.split_spaces()
        assert_equal(x[0], nd, msg='Empty node does not split into itself')

        nd = SearchTreeNode('test', exclusive=True)
        x = nd.split_spaces()
        assert_equal(x[0], nd, msg='Empty node does not split into itself')

        nd = SearchTreeNode('test', optional=True)
        x = nd.split_spaces()
        assert_equal(x[0], nd, msg='Empty node does not split into itself')

        nd = SearchTreeNode('test', exclusive=True, optional=True)
        x = nd.split_spaces()
        assert_equal(x[0], nd, msg='Empty node does not split into itself')

        # Test with child nodes
        kids = [SearchTreeLeaf('const', value=ConstantSpace(1)),
                SearchTreeLeaf('disc', value=DiscreteSpace(values=[1, 2, 3, 4, 5])),
                SearchTreeLeaf('cont', value=ContinuousSpace())]

        # Test splitting with child nodes, following all children
        nd = SearchTreeNode('test', children=kids)
        x = nd.split_spaces()
        assert_equal(x[0], nd, msg='Non-exclusive node does not split into itself')

        # Test splitting with child nodes, following all children and optional
        nd = SearchTreeNode('test', children=kids, optional=True)
        x = nd.split_spaces()
        assert_equal(len(x), 2, msg='Optional version was not generated')
        assert_equal(x[0], nd, msg='Non-optional part was not created')
        nd_opt = SearchTreeNode('test', optional=True)
        assert_equal(x[1], nd_opt, msg='Optional part was not created empty')

        # Test splitting with child nodes, following one child
        nd = SearchTreeNode('test', children=kids, exclusive=True)
        x = nd.split_spaces()
        assert_equal(len(x), 3, msg='Optional version was not generated')
        nd_0 = SearchTreeNode('test', children=[kids[0]], exclusive=True)
        assert_equal(x[0], nd_0, msg='Exclusive branch tree was not created')
        nd_1 = SearchTreeNode('test', children=[kids[1]], exclusive=True)
        assert_equal(x[1], nd_1, msg='Exclusive branch tree was not created')
        nd_2 = SearchTreeNode('test', children=[kids[2]], exclusive=True)
        assert_equal(x[2], nd_2, msg='Exclusive branch tree was not created')

        # Test splitting with child nodes, following one child and optional
        nd = SearchTreeNode('test', children=kids, exclusive=True, optional=True)
        x = nd.split_spaces()
        assert_equal(len(x), 4, msg='Optional version was not generated')
        nd_0 = SearchTreeNode('test', children=[kids[0]], exclusive=True, optional=True)
        assert_equal(x[0], nd_0, msg='Exclusive branch tree was not created')
        nd_1 = SearchTreeNode('test', children=[kids[1]], exclusive=True, optional=True)
        assert_equal(x[1], nd_1, msg='Exclusive branch tree was not created')
        nd_2 = SearchTreeNode('test', children=[kids[2]], exclusive=True, optional=True)
        assert_equal(x[2], nd_2, msg='Exclusive branch tree was not created')
        nd_opt = SearchTreeNode('test', exclusive=True, optional=True)
        assert_equal(x[3], nd_opt, msg='Optional part was not created empty')

        # Complicated test incorporating everything
        kid_0 = SearchTreeLeaf('const', value=ConstantSpace(0))
        kid_1 = SearchTreeLeaf('const', value=ConstantSpace(1))
        kid_2 = SearchTreeLeaf('const', value=ConstantSpace(2))
        kid_3 = SearchTreeLeaf('const', value=ConstantSpace(3))
        kid_4 = SearchTreeLeaf('const', value=ConstantSpace(4))
        kid_5 = SearchTreeLeaf('const', value=ConstantSpace(5))
        kid_6 = SearchTreeLeaf('const', value=ConstantSpace(6))
        kid_7 = SearchTreeLeaf('const', value=ConstantSpace(7))
        kid_8 = SearchTreeLeaf('const', value=ConstantSpace(8))

        a = SearchTreeNode('all', children=[kid_0, kid_1])
        ao = SearchTreeNode('all_opt', children=[kid_2, kid_3], optional=True)
        o = SearchTreeNode('opt', children=[kid_4], optional=True)
        eo = SearchTreeNode('exc_opt', children=[kid_5, kid_6], exclusive=True, optional=True)
        e = SearchTreeNode('exc', children=[kid_7, kid_8], exclusive=True)

        A = SearchTreeNode('All', children=[a, ao])
        E = SearchTreeNode('Exc', children=[o, eo, e], exclusive=True)

        root = SearchTreeNode('root', children=[A, E])

        x = root.split_spaces()
        assert_equal(len(x), 14, msg='Incorrect number of trees generated')


class TestSearchTree(object):
    def test_init(self):
        # Test default initialization
        st = SearchTree()
        assert_is_none(st.root, msg='Default root not set')
        assert_dict_equal(st.values, {}, msg='Default values not set')
        assert_equal(st.priority, 1.0, msg='Default priority not set')
        assert_equal(st.complexity, -1.0, msg='Default complexity not set')

        # Test initialization with SearchTreeNode as root
        kids = [SearchTreeLeaf('const', value=ConstantSpace(1)),
                SearchTreeLeaf('disc', value=DiscreteSpace(values=[1, 2, 3, 4, 5])),
                SearchTreeLeaf('cont', value=ContinuousSpace())]
        nd = SearchTreeNode('test', children=kids)
        st = SearchTree(root=nd)
        assert_equal(st.root, nd, msg='Passed root not set')
        assert_dict_equal(st.values, {}, msg='Default values not set')
        assert_equal(st.priority, 1.0, msg='Default priority not set')
        c = sum([k.complexity() for k in kids])
        assert_equal(st.complexity, c, msg='Default complexity not set')

        # Test initialization with SearchTreeLeaf as root
        r = SearchTreeLeaf('disc', value=DiscreteSpace(values=[1, 2, 3, 4, 5]))
        st = SearchTree(root=r)
        r = SearchTreeNode('root', children=[r])
        assert_equal(st.root, r, msg='Passed root not set')
        assert_dict_equal(st.values, {}, msg='Default values not set')
        assert_equal(st.priority, 1.0, msg='Default priority not set')
        assert_equal(st.complexity, r.complexity(), msg='Default complexity not set')

        # Test initializing with values
        st = SearchTree(values=[1, 2, 3, 4, 5])
        assert_is_none(st.root, msg='Default root not set')
        assert_list_equal(st.values, [1, 2, 3, 4, 5], msg='Passed values not set')
        assert_equal(st.priority, 1.0, msg='Default priority not set')
        assert_equal(st.complexity, -1.0, msg='Default complexity not set')

        # Test initializing with priority
        st = SearchTree(priority=2.7)
        assert_is_none(st.root, msg='Default root not set')
        assert_dict_equal(st.values, {}, msg='Default values not set')
        assert_equal(st.priority, 2.7, msg='Passed priority not set')
        assert_equal(st.complexity, -1.0, msg='Default complexity not set')

        def test_flatten_param(self):
            p = {
                    'A': {
                        'a': 1,
                        'b': 2
                    },
                    'B': {
                        'c': {
                            'e': 5
                            },
                        'd': 4
                        }
                }

            p_flat = {'A_a': 1, 'A_b': 2, 'B_c_e': 5, 'B_d': 4}

            st = SearchTree()
            x = st.flatten_param(p)
            print(x)
            assert_dict_equal(x, p, msg='dict did not flatten correctly')
