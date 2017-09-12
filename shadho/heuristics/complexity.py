"""Functions for calculating relative search complexity.
"""
import scipy.stats
import numpy as np


def complexity(space):
    if hasattr(space, 'dist') and \
       isinstance(space.dist, scipy.stats.rv_continuous):
        a, b = space.interval(0.9999)
        d = np.linalg.norm(b - a)
        return 2 + d
    elif isinstance(space, list) and len(space) > 0:
        return 2.0 - (1.0 / float(len(space)))
    else:
        return 1
