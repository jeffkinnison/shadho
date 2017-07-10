"""Functions for calculating rellative search complexity.
"""
from .check import heuristic_check

import scipy.stats
import numpy


@heuristic_check
def complexity(space):
    if isinstance(space.domain, scipy.stats.rv_continuous):
        a, b = space.domain.interval(0.9999)
        d = np.linalg.norm(b - a)
        return 2 + d
    elif isinstance(space.domain, list):
        return 2 - (1 / len(space.domain))
    else:
        return 1
