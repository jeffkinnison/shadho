"""Functions for calculating rellative search complexity.
"""
from .check import heuristic_check

import scipy.stats
import numpy as np


#@heuristic_check
def complexity(space):
    if hasattr(space, 'dist') and isinstance(space.dist, scipy.stats.rv_continuous):
        a, b = space.interval(0.9999)
        d = np.linalg.norm(b - a)
        return 2 + d
    elif isinstance(space, list) and len(space) > 0:
        return 2 - (1 / len(space))
    else:
        return 1
