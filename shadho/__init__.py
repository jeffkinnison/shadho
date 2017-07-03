# -*- coding: utf-8 -*-
"""Package-level imports for SHADHO.

Modules
-------
config: helper classes for configuring Work Queue (master and tasks)
forest: implementation of the Ordered Search Forest data structure
hardware: tools for grouping hardware by common resource attributes
helpers: helper functions for defining search spaces
scales: functions for scaling numeric search values
shadho: the main distributed hyperparameter search driver
spaces: classes defining discrete and continuous search spaces
strategies: functions defining how to choose values from a search space
tree: tree data structures for implementing the Ordered Search Forest
"""

# Package-level imports, chosen because they are what will typically be
# accessed by the user.
from .shadho import HyperparameterSearch
from .forest import OrderedSearchForest
from .hardware import ComputeClass
from .config import SHADHOConfig, WQFile
from .helpers import uniform, ln_uniform, log10_uniform, log2_uniform
from .helpers import normal, ln_normal, log10_normal, log2_normal
from .helpers import randint, log10_randint, log2_randint
from .helpers import choose

from .backends import JSONBackend, SQLBackend

class BackendNotSupported(Exception):
    pass

config = SHADHOConfig()

b = {
    'json': JSONBackend,
    'sql': SQLBackend
}

try:
    name = config.config.get('backend', 'type')
    backend = b[name]()
except KeyError:
    raise BackendNotSupported('{} is not a supported SHADHO backend'
                              .format(name))

del name

__all__ = [HyperparameterSearch, OrderedSearchForest, ComputeClass,
           WQFile, uniform, ln_uniform, log10_uniform, log2_uniform, normal,
           ln_normal, log10_normal, log2_normal, randint, log10_randint,
           log2_randint, choose]
