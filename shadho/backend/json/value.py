from shadho.backend.base.value import BaseValue

import uuid


class Value(BaseValue):
    def __init__(self, id=None, value=None, domain=None, result=None):
        self.id = id if id is not None else str(uuid.uuid4())
        self.value = value
        self.domain = domain.id if hasattr(domain, 'id') else domain
        self.result = result.id if hasattr(result, 'id') else result

    def to_json(self):
        return {
            'value': self.value,
            'domain': self.domain,
            'result': self.result,
        }
