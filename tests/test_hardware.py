from shadho import ComputeClass

from nose.tools import assert_equal, assert_is, assert_is_instance
from nose.tools import assert_list_equal, raises, assert_is_none


class TestComputeClass(object):
    def test_init(self):
        # Test the default initialization
        cc = ComputeClass('test', 'key', 'val', 'echo')
        assert_equal(cc.name, 'test', msg='Name not set correctly')
        assert_equal(cc.resource, 'key', msg='Resource not set correctly')
        assert_equal(cc.value, 'val', msg='Value not set correctly')

        cc = ComputeClass('test2', 'key2', 'val2', 'echo')
        assert_equal(cc.name, 'test2', msg='Name not set correctly')
        assert_equal(cc.resource, 'key2', msg='Resource not set correctly')
        assert_equal(cc.value, 'val2', msg='Value not set correctly')
