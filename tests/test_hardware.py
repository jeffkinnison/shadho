import pytest

from scipy.stats import uniform

from shadho.hardware import ComputeClass

import sys

from pyrameter.modelgroup import ModelGroup
from pyrameter.models.model import Model
from pyrameter.models.random_search import RandomSearchModel
from pyrameter.models.gp import GPBayesModel
from pyrameter.domain import Domain, DiscreteDomain, ContinuousDomain


class TestComputeClass(object):

    __discrete_domain__ = [1, 2, 3, 4, 5]

    def test_init(self):

        # Test initialization of Compute Class object
        cc = ComputeClass("name", "resource", 1, 100)

        assert cc.name == "name"
        assert cc.resource == "resource"
        assert cc.value == 1
        assert cc.max_tasks == 100
        assert not cc.model_group

    def test_generate(self):

        # Test single model - with single DiscreteDomain
        m = RandomSearchModel(id=1)
        m.add_domain(DiscreteDomain(self.__discrete_domain__))

        cc = ComputeClass("name", "resource", 2, 100)
        cc.model_group = ModelGroup(m)

        result = cc.generate(m.id)
        print(result)

        assert result[0] == m.id
        assert result[1] == m.results[0].id
        assert isinstance(result[-1][''], int)
        assert result[2][''] in self.__discrete_domain__

        # Test single model - with single ContinuousDomain
        m = RandomSearchModel(id=1)
        m.add_domain(ContinuousDomain(uniform, loc=1.0, scale=5.0))

        cc = ComputeClass("name", "resource", 2, 100)
        cc.model_group = ModelGroup(m)

        result = cc.generate(1)

        assert isinstance(result[-1][''], float)
        assert result[-1][''] >= 1.0 and result[-1][''] <= 6.0

        # Test single model - with multiple Domains
        m = RandomSearchModel(id=1)
        m.add_domain(DiscreteDomain(self.__discrete_domain__, path='a'))
        m.add_domain(ContinuousDomain(uniform, path='b', loc=1.0, scale=5.0))

        cc = ComputeClass("name", "resource", 2, 100)
        cc.model_group = ModelGroup(m)

        result = cc.generate(1)

        assert isinstance(result[-1]['a'], int)
        assert result[-1]['a'] in self.__discrete_domain__
        assert isinstance(result[-1]['b'], float)
        assert result[-1]['b'] >= 1.0 and result[-1]['b'] <= 6.0

        # Test multiple models
        m1 = RandomSearchModel(id=1)
        m1.add_domain(DiscreteDomain(self.__discrete_domain__))

        m2 = GPBayesModel(id=2)
        m2.add_domain(DiscreteDomain(self.__discrete_domain__))

        cc = ComputeClass("name", "resource", 2, 100)
        cc.model_group = ModelGroup(m1)
        cc.model_group.add_model(m2)

        result1 = cc.generate(1)
        result2 = cc.generate(2)

        assert isinstance(result1[-1][''], int)
        assert result1[-1][''] in self.__discrete_domain__
        assert isinstance(result2[-1][''], int)
        assert result2[-1][''] in self.__discrete_domain__

    def test_add_model(self):
        m1 = Model(id=1)

        cc = ComputeClass("name", "resource", 1, 100)

        cc.add_model(m1)

        assert len(cc.model_group.models.keys()) == 1

    def test_remove_model(self):
        m1 = Model(id=1)

        cc = ComputeClass("name", "resource", 1, 100)

        cc.model_group = ModelGroup(m1)
        assert len(cc.model_group.models.keys()) == 1

        cc.remove_model(1)
        assert len(cc.model_group.models.keys()) == 0

    def test_clear(self):
        models = [Model(id=i) for i in range(100)]

        # Test clearing an empty CC (nothing should happen)
        cc = ComputeClass('name', 'resource', 1, 100)
        assert len(cc.model_group) == 0
        cc.clear()
        assert len(cc.model_group) == 0

        # Test clearing a single- and multi-model ModelGroup
        for i in range(1, len(models)):
            cc.model_group = ModelGroup(models=models[:i])
            assert len(cc.model_group) == i
            cc.clear()
            assert len(cc.model_group) == 0
