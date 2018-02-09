from shadho.backend.base.model import BaseModel
from shadho.backend.json.domain import Domain
from shadho.backend.json.result import Result
from shadho.backend.utils import InvalidObjectError

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

        domains = [domains] if not isinstance(domains, list) else domains
        results = [results] if not isinstance(results, list) else results
        for domain in domains:
            self.add_domain(domain)
        for result in results:
            self.add_result(result)

    def add_domain(self, domain):
        if domain is not None:
            if isinstance(domain, Domain):
                self.domains.append(domain.id)
            elif isinstance(domain, (int, str)):
                self.domains.append(domain)
            else:
                raise InvalidObjectError(domain)

    def add_result(self, result):
        if result is not None:
            if isinstance(result, Result):
                self.results.append(result.id)
            elif isinstance(result, (int, str)):
                self.results.append(result)
            else:
                raise InvalidObjectError(result)

    def to_json(self):
        return {
            'priority': self.priority,
            'complexity': self.complexity,
            'rank': self.rank,
            'domains': self.domains,
            'results': self.results,
        }
