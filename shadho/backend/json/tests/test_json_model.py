import pytest

from shadho.backend.json.model import Model
from shadho.backend.json.domain import Domain
from shadho.backend.json.result import Result
from shadho.backend.utils import InvalidObjectError

from shadho.backend.base.tests.test_base_model import TestBaseModel

import uuid


class TestJsonModel(TestBaseModel):
    __model_class__ = Model
    __domain_class__ = Domain
    __result_class__ = Result

    def test_init(self):
        # Test the default initialization
        m = self.__model_class__()
        assert m.id is not None
        assert isinstance(m.id, str)
        assert m.priority is None
        assert m.complexity is None
        assert m.rank is None
        assert m.domains == []
        assert m.results == []

        # Test with custom id, priority, complexity, rank, domains, results
        d = self.__domain_class__()
        r = self.__result_class__()
        mid = str(uuid.uuid4())
        m = self.__model_class__(id=mid, priority=1,
                                 complexity=1, rank=1, domains=[d],
                                 results=[r])
        assert m.id == mid
        assert m.priority == [1]
        assert m.complexity == 1
        assert m.rank == 1
        assert m.domains == [d.id]
        assert m.results == [r.id]

        # Test using floating point priority, domain id, result id
        m = self.__model_class__(priority=1.43, domains=[d.id], results=[r.id])
        assert m.priority == [1.43]
        assert m.domains == [d.id]
        assert m.results == [r.id]

        # Test using list for priority, single domain object, result object
        m = self.__model_class__(priority=[1.43], domains=d, results=r)
        assert m.priority == [1.43]
        assert m.domains == [d.id]
        assert m.results == [r.id]

        # Test using a single domain and result id
        m = self.__model_class__(domains=d.id, results=r.id)
        assert m.domains == [d.id]
        assert m.results == [r.id]

        # Test using invalid domain and result values
        invalids = [self.__model_class__(), (1,), {'1': 1}]
        for i in invalids:
            with pytest.raises(InvalidObjectError):
                self.__model_class__(domains=i)
            with pytest.raises(InvalidObjectError):
                self.__model_class__(results=i)

    def test_add_domain(self):
        m = self.__model_class__()

        d1 = self.__domain_class__()
        d2 = self.__domain_class__()

        # Test adding a domain class
        m.add_domain(d1)
        assert m.domains == [d1.id]

        # Test adding a domain id
        m.add_domain(d2.id)
        assert m.domains == [d1.id, d2.id]

        # Test adding invalid objects
        invalids = [self.__model_class__(), (1,), {'1': 1}]
        for i in invalids:
            print(i)
            with pytest.raises(InvalidObjectError):
                m.add_domain(i)
            assert m.domains == [d1.id, d2.id]

    def test_add_result(self):
        m = self.__model_class__()

        r1 = self.__result_class__()
        r2 = self.__result_class__()

        # Test adding a result class
        m.add_result(r1)
        assert m.results == [r1.id]

        # Test adding a result id
        m.add_result(r2.id)
        assert m.results == [r1.id, r2.id]

        # Test adding invalid objects
        invalids = [self.__model_class__(), (1,), {'1': 1}]
        for i in invalids:
            with pytest.raises(InvalidObjectError):
                m.add_result(i)
            assert m.results == [r1.id, r2.id]

    def test_to_json(self):
        # Test with default initialization
        m = self.__model_class__()
        correct = {
            'priority': None,
            'complexity': None,
            'rank': None,
            'domains': [],
            'results': []
        }
        assert m.to_json() == correct

        # Test with custom id, priority, complexity, rank, domains, results
        d = self.__domain_class__()
        r = self.__result_class__()
        mid = str(uuid.uuid4())
        m = self.__model_class__(id=mid, priority=1,
                                 complexity=1, rank=1, domains=[d],
                                 results=[r])
        correct = {
            'priority': [1],
            'complexity': 1,
            'rank': 1,
            'domains': [d.id],
            'results': [r.id]
        }
        assert m.to_json() == correct

        # Test using floating point priority, domain id, result id
        m = self.__model_class__(priority=1.43, domains=[d.id], results=[r.id])
        correct = {
            'priority': [1.43],
            'complexity': None,
            'rank': None,
            'domains': [d.id],
            'results': [r.id]
        }
        assert m.to_json() == correct

        # Test using list for priority, single domain object, result object
        m = self.__model_class__(priority=[1.43], domains=d, results=r)
        correct = {
            'priority': [1.43],
            'complexity': None,
            'rank': None,
            'domains': [d.id],
            'results': [r.id]
        }
        assert m.to_json() == correct

        # Test using a single domain and result id
        m = self.__model_class__(domains=d.id, results=r.id)
        correct = {
            'priority': None,
            'complexity': None,
            'rank': None,
            'domains': [d.id],
            'results': [r.id]
        }
        assert m.to_json() == correct
