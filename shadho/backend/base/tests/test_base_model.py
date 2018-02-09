import pytest

from shadho.backend.base.model import BaseModel
from shadho.backend.base.domain import BaseDomain
from shadho.backend.base.result import BaseResult


class TestBaseModel(object):
    __model_class__ = BaseModel
    __domain_class__ = BaseDomain
    __result_class__ = BaseResult

    def test_tablename(self):
        # The model tablename should be 'models'
        m = self.__model_class__()
        assert m.__tablename__ == 'models'

    def test_add_domain(self):
        # add_domain() should not be implemented for this class
        m = self.__model_class__()
        d = self.__domain_class__()

        with pytest.raises(NotImplementedError):
            m.add_domain(d)

    def test_add_result(self):
        # add_result() should not be implemented for this class
        m = self.__model_class__()
        r = self.__result_class__()

        with pytest.raises(NotImplementedError):
            m.add_result(r)
