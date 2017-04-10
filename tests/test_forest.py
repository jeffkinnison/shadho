from shadho.forest import OrderedSearchForest
from shadho.tree import SearchTree, SearchTreeNode, SearchTreeLeaf
from shadho.spaces import BaseSpace, ConstantSpace, ContinuousSpace, DiscreteSpace

from nose.tools import assert_equal, assert_list_equal


class TestOrderedSearchForest(object):
    def test_init(self):
        # Test on empty spec
        sf = OrderedSearchForest({})
        st = SearchTree(root=SearchTreeNode('root'))
        assert_equal(len(sf.trees), 1, msg='Too many trees from spec!')

        # Test on simple spec
        spec = {
            'val': 4,
            'const': ConstantSpace(5),
            'disc': DiscreteSpace(values=[1, 2, 3, 4, 5]),
            'cont': ContinuousSpace()
        }
        sf = OrderedSearchForest(spec)
        nd = SearchTreeNode('root')
        nd.add_child(SearchTreeLeaf('val', ConstantSpace(4)))
        nd.add_child(SearchTreeLeaf('const', ConstantSpace(5)))
        nd.add_child(SearchTreeLeaf('disc', DiscreteSpace(values=[1,2,3,4,5])))
        nd.add_child(SearchTreeLeaf('cont', ContinuousSpace()))
        st = SearchTree(root=nd)
        assert_equal(len(sf.trees), 1, msg='Too many trees from spec!')

        # Test on exclusive spec
        spec['optional'] = True
        sf = OrderedSearchForest(spec)
        assert_equal(len(sf.trees), 2, msg="Incorrect number of trees")

        # Test on exclusive spec
        spec['optional'] = False
        spec['exclusive'] = True
        sf = OrderedSearchForest(spec)
        assert_equal(len(sf.trees), 4, msg="Incorrect number of trees")

        # Test on exclusive spec
        spec['optional'] = True
        spec['exclusive'] = True
        sf = OrderedSearchForest(spec)
        assert_equal(len(sf.trees), 5, msg="Incorrect number of trees")
