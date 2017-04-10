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
from .helpers import uniform, ln_uniform, log10_uniform, log2_uniform
from .helpers import normal, ln_normal, log10_normal, log2_normal
from .helpers import randint, log10_randint, log2_randint
from .helpers import choose

__all__ = [HyperparameterSearch, OrderedSearchForest, ComputeClass, uniform,
           ln_uniform, log10_uniform, log2_uniform, normal, ln_normal,
           log10_normal, log2_normal, randint, log10_randint, log2_randint,
           choose]
