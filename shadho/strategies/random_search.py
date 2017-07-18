"""
"""

import scipy.stats.rv_continuous
import scipy.stats.randint


def random(space):
    if isinstance(space.domain, scipy.stats.rv_continuous):
        return space.domain.rvs()
    elif isinstance(space.domain, list):
        return space.domain[scipy.stats.randint.rvs(0, len(space.domain))]
    else:
        return space.domain
