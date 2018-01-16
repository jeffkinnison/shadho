from shadho.backend.base.domain import BaseDomain
from shadho.backend.json.value import Value

import uuid


class Domain(BaseDomain):
    def __init__(self, id=None, domain=None, path=None, strategy=None,
                 scaling=None, model=None, values=None, exhaustive=False,
                 exhaustive_idx=None):
        self.id = id if id is not None else str(uuid.uuid4())
        self.exhaustive_idx = exhaustive_idx
        if isinstance(domain, dict):
            distribution = getattr(scipy.stats, domain['distribution'])
            self.domain = distribution(*domain['args'],
                                       **domain['kwargs'])
            rng = np.random.RandomState()
            if 'rng' in domain:
                state = domain['rng']
                rng.set_state(tuple([state[0], np.array(state[1]), state[2],
                                     state[3], state[4]]))
            self.domain.random_state = rng
        elif exhaustive and isinstance(domain, list) and exhaustive_idx is None:
            self.domain = domain
            self.exhaustive_idx = 0
        else:
            self.domain = domain

        self.exhaustive = exhaustive

        self.path = path

        self.strategy = strategy if strategy is not None else 'random'
        self.scaling = scaling if scaling is not None else 'linear'

        self.model = model.id if hasattr(model, 'id') else model

        self.values = [] if values is None or len(values) == 0 else values
        values = values if values is not None else []
        for value in values:
            self.add_value(value)

    def add_value(self, value):
        if isinstance(value, Value):
            self.values.append(value.id)
        elif isinstance(value, (int, str)):
            self.values.add(value)
        else:
            raise InvalidObjectClassError

    def to_json(self):
        if hasattr(self.domain, dist):
            domain = {
                'domain': self.domain.dist.name,
                'args': self.domain.args,
                'kwargs': self.domain.kwds,
            }
        else:
            domain = self.domain

        return {
            'domain': domain,
            'path': self.path,
            'strategy': self.strategy,
            'scaling': self.scaling,
            'model': self.model,
            'values': self.values,
            'exhaustive': self.exhaustive,
            'exhaustive_idx': self.exhaustive_idx
        }
