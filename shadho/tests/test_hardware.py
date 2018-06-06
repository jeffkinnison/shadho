import pytest

from shadho.hardware import ComputeClass
from shadho import rand
import sys
sys.path.append("../pyrameter")
from pyrameter.models.model import Model
from pyrameter.domain import Domain, DiscreteDomain, ContinuousDomain

class TestComputeClass(object):
    __discrete_class__ = DiscreteDomain
    __default_discrete__ = [1, 2, 3, 4, 5]
    __continuous_class__ = ContinuousDomain
    __default_continuous__ = rand.uniform(1, 5)
    __model_class__ = Model
    
    def test_init(self):

        # Test single model with single DiscreteDomain
        d = self.__discrete_class__(self.__default_discrete__)

        m = self.__model_class__(id=1)
        m.add_domain(d)

        cc = ComputeClass("class_name", "resource", 1, 100, m)

        assert cc.name == "class_name"
        assert cc.resource == "resource"
        assert cc.value == 1
        assert cc.max_tasks == 100

        assert isinstance(cc.model_group.models, dict)
        assert cc.model_group.models[1].domains[0].domain == self.__default_discrete__ 
  
        # Test single model with single ContinuousDomain
        d = self.__continuous_class__

    def test_generate(self):
        pass

    def test_add_model(self):
        pass

    def test_remove_model(self):
        pass
