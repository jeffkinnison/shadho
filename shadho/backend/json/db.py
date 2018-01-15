from shadho.backend.base.db import BaseBackend
from shadho.backend.json.model import Model
from shadho.backend.json.domain import Domain
from shadho.backend.json.result import Result
from shadho.backend.json.value import Value

import json
import os


class JsonBackend(BaseBackend):
    """Data management and storage backend based on JSON.

    Parameters
    ----------
    path : str, optional
        Path to the directory to write data.

    Attributes
    ----------
    path : str
        Path to the directory to write data.
    db : dict
        In-memory dictionary containing search data.

    """

    data_classes = {
        'models': Model,
        'domains': Domain,
        'results': Result,
        'values': Value
    }

    def __init__(self, path='shadho.json', commit_frequency=10, update_frequency=10):
        self.path = os.path.abspath(path)
        if os.path.isdir(self.path):
            self.path = os.path.join(self.path, 'shadho.json')

        self.db = {
            'models': {},
            'domains': {},
            'results': {},
            'values': {}
        }
        super(JsonBackend, self).__init__(commit_frequency=commit_frequency,
                                          update_frequency=update_frequency)

    def commit(self):
        with open(self.path, 'w') as f:
            json.dump(self.db, f)

    def count(self, objclass):
        if objclass in self.db:
            return len(self.db['objclass'])
        else:
            raise InvalidObjectClassError(objclass)

    def create(self, objclass, *args, **kwargs):
        if objclass in self.data_classes:
            return self.data_classes[objclass](*args, **kwargs)
        else:
            raise InvalidObjectClassError(objclass)

    def delete(self, obj):
        if hasattr(obj, '__tablename__') and obj.__tablename__ in self.db:
            if obj.id in self.db[obj.__tablename__]:
                del self.db[obj.__tablename__][obj.id]

    def find(self, objclass, oid):
        if objclass in self.db:
            if oid in self.db[objclass]:
                return self.create(objclass, **self.db[objclass], oid)
            else:
                return None
        else:
            raise InvalidObjectClassError

    def find_all(self, objclass):
        if objclass in self.db:
            return list(map(lambda o: self.create(objclass, **o),
                            self.db[objclass].values()))
        else:
            raise InvalidObjectClassError

    def update(self, obj):
        if hasattr(obj, '__tablename__') and obj.__tablename__ in self.db:
            if hasattr(obj, 'id'):
                self.db[obj.__tablename__][obj.id] = obj.to_json()
            else:
                raise InvalidObjectError
        else:
            raise InvalidObjectClassError(obj.__tablename__)
