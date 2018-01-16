import pytest

from shadho.backend.base.domain import BaseDomain
from shadho.backend.base.result import BaseResult
from shadho.backend.base.value import BaseValue

import numpy as np
import scipy.stats


class TestBaseResult(object):
    """Unit tests for the BaseResult class"""

    __domain_class__ = BaseDomain
    __result_class__ = BaseResult
    __value_class__ = BaseValue

    def test_tablename(self):
        """Ensure that BaseResult instances have the correct table name."""
        assert self.__result_class__.__tablename__ == 'results'

    def test_add_value(self):
        """Ensure that BaseResult does not implement an add_value method."""
        r = self.__result_class__()

        with pytest.raises(NotImplementedError):
            r.add_value(self.__value_class__)
