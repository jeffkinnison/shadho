import pytest

from shadho.backend.base.value import BaseValue


class TestBaseValue(object):
    """Unit tests for the BaseValue class"""

    __value_class__ = BaseValue

    def test_tablename(self):
        """Ensure that BaseValue instances have the correct table name."""
        assert self.__value_class__.__tablename__ == 'values'
