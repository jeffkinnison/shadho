from shadho.backend.base.value import BaseValue

import uuid


class Value(BaseValue):
    def __init__(self, id=None, value=None, space=None, result=None):
        self.id = id if id is not None else str(uuid.uuid4())
        self.value = value
        self.space = space.id if isinstance(space, Space) else space
        self.result = result.id if isinstance(result, Result) else result

    def to_json(self):
        return {
            'value': self.value,
            'space': self.space,
            'result': self.result,
        }
