from shadho.backend.base.model import BaseModel
from shadho.backend.json.domain import Domain
from shadho.backend.json.result import Result

import uuid


class Model(BaseModel):
    def __init__(self, id=None, priority=None, complexity=None, rank=None,
                 domains=None, results=None):
        self.id = id if id is not None else str(uuid.uuid4())
        self.priority = [priority] if isinstance(priority, (int, float)) \
                        else priority
        self.complexity = complexity
        self.rank = rank
        self.domains = []
        self.results = []
        map(self.add_domain, domains if domains is not None else [])
        map(self.add_result, results if results is not None else [])

    def add_domain(self, domain):
        if isinstance(domain, Domain):
            self.domains.append(domain.id)
        elif isinstance(domain, (int, str)):
            self.domains.append(domain)

    def add_result(self, result):
        if isinstance(result, Result):
            self.results.append(result.id)
        elif isinstance(result, (int, str)):
            self.results.append(result)

    def to_json(self):
        return {
            'priority': self.priority,
            'complexity': self.complexity,
            'rank': self.rank,
            'domains': self.spaces,
            'results': self.results,
        }
