from shadho import ComputeClass

from nose.tools import assert_equal, assert_is, assert_is_instance
from nose.tools import assert_list_equal, raises, assert_is_none


class TestComputClass(object):
    def test_init(self):
        # Test the default initialization
        cc = ComputeClass('test', 'key', 'val', 50)
        assert_equal(cc.name, 'test', msg='Name not set correctly')
        assert_equal(cc.resource, 'key', msg='Resource not set correctly')
        assert_equal(cc.value, 'val', msg='Value not set correctly')
        assert_equal(cc.max_tasks, 50, msg='Max tasks not set correctly')
        assert_equal(cc.submitted_tasks, 0, msg='Submitted tasks not set correctly')
        assert_list_equal(cc.assignments, [], msg='Default empty assignments not set')

        # Test passing assignments
        assignments = ['a', 'b', 'c']
        cc = ComputeClass('test2', 'key2', 'val2', 99, assignments=assignments)
        assert_equal(cc.name, 'test2', msg='Name not set correctly')
        assert_equal(cc.resource, 'key2', msg='Resource not set correctly')
        assert_equal(cc.value, 'val2', msg='Value not set correctly')
        assert_equal(cc.max_tasks, 99, msg='Max tasks not set correctly')
        assert_equal(cc.submitted_tasks, 0, msg='Submitted tasks not set correctly')
        assert_is(cc.assignments, assignments, msg='Passed assignments not set')

    def test_clear_assignments(self):
        # Test with no assignments
        cc = ComputeClass('test', 'key', 'val', 50)
        cc.clear_assignments()
        assert_list_equal(cc.assignments, [], msg='Empty list not cleared')

        # Test with assignments
        assignments = ['a', 'b', 'c']
        cc = ComputeClass('test2', 'key2', 'val2', 99, assignments=assignments)
        cc.clear_assignments()
        assert_list_equal(cc.assignments, [], msg='Assignments not cleared')

    def test_assign(self):
        cc = ComputeClass('test', 'key', 'val', 50)
        cc.assign(None)
        assert_is_none(cc.assignments[-1], msg='None not assigned')

        cc.assign(1)
        assert_equal(cc.assignments[-1], 1, msg='1 not assigned')
        assert_is_instance(cc.assignments[-1], int, msg='assignment type changed')
