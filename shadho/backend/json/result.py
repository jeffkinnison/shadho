from shadho.backend.base.result import BaseResult
from shadho.backend.json.value import Value

import uuid


class Result(BaseResult):
    def __init__(self, id=None, loss=None, results=None, submissions=None,
                 model=None, values=None):
        self.id = id if id is not None else str(uuid.uuid4())
        self.loss = loss
        self.results = results
        self.submissions = submissions if submissions is not None else 0
        self.model = model.id if hasattr(model, 'id') else model

        self.values = []
        map(self.add_value, values if values is not None else [])

    def add_value(self, value):
        if isinstance(value, Value):
            self.values.append(value.id)
        elif isinstance(value, (int, str)):
            self.values.add(value)
        else:
            raise InvalidObjectClassError

    def to_json(self):
        return {
            'loss': self.loss,
            'results': self.results,
            'model': self.model,
            'values': self.values,
        }
