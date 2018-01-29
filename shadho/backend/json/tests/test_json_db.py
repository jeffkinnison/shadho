import pytest

from shadho.backend.base.tests.test_base_db import TestBaseBackend
from shadho.backend.json.db import JsonBackend
from shadho.backend.json.model import Model
from shadho.backend.json.domain import Domain
from shadho.backend.json.result import Result
from shadho.backend.json.value import Value
from shadho.backend.utils import InvalidObjectClassError, InvalidObjectError

import json
import os
import shutil
import tempfile


class TestJsonBackend(object):

    def test_init(self):
        """Ensure that initialization sets up the db and filepath."""
        # Test default initialization
        b = JsonBackend()
        assert b.path == os.path.join(os.getcwd(), 'shadho.json')
        assert b.db == {'models': {},
                        'domains': {},
                        'results': {},
                        'values': {}}
        assert b.commit_frequency == 10
        assert b.update_frequency == 10

        # Test custom initialization
        b = JsonBackend(path='foo.bar',
                        commit_frequency=42,
                        update_frequency=42)
        assert b.path == os.path.join(os.getcwd(), 'foo.bar')
        assert b.db == {'models': {},
                        'domains': {},
                        'results': {},
                        'values': {}}
        assert b.commit_frequency == 42
        assert b.update_frequency == 42

        # Test without specifying a file name
        b = JsonBackend(path='/tmp')
        assert b.path == os.path.join('/tmp', 'shadho.json')
        assert b.db == {'models': {},
                        'domains': {},
                        'results': {},
                        'values': {}}
        assert b.commit_frequency == 10
        assert b.update_frequency == 10

    def test_commit(self):
        """Ensure that commit writes to file and the file is loadable."""
        temp = tempfile.mkdtemp()
        fpath = os.path.join(temp, 'shadho.json')

        # Test saving and loading
        b = JsonBackend(path=temp)
        b.commit()
        assert os.path.isfile(fpath)
        with open(fpath, 'r') as f:
            db = json.load(f)
            assert db == {'models': {},
                          'domains': {},
                          'results': {},
                          'values': {}}

        shutil.rmtree(temp)

    def test_count(self):
        """Ensure that the correct counts are returned for object classes"""
        # Test count on empty database
        b = JsonBackend()
        assert b.count('models') == 0
        assert b.count('domains') == 0
        assert b.count('results') == 0
        assert b.count('values') == 0

        b.db['models'] = {str(i): i for i in range(10)}
        b.db['domains'] = {str(i): i for i in range(20)}
        b.db['results'] = {str(i): i for i in range(30)}
        b.db['values'] = {str(i): i for i in range(40)}
        assert b.count('models') == 10
        assert b.count('domains') == 20
        assert b.count('results') == 30
        assert b.count('values') == 40

        with pytest.raises(InvalidObjectClassError):
            b.count('foo')

    def test_create(self):
        """Ensure objects are created and instantied correctly."""
        b = JsonBackend()

        # Test creating standard objects with no args
        model = b.create('models')
        domain = b.create('domains')
        result = b.create('results')
        value = b.create('values')

        assert isinstance(model, Model)
        assert isinstance(domain, Domain)
        assert isinstance(result, Result)
        assert isinstance(value, Value)
