import pytest

from shadho.heuristics import complexity

import numpy as np
import scipy.stats


def test_complexity():
    # Test complexity of constant domains
    assert complexity(None) == 1
    assert complexity(1.7) == 1
    assert complexity(1) == 1
    assert complexity('foo') == 1
    assert complexity(-84576) == 1

    # Test complexityof discrete domains
    assert complexity([]) == 1
    assert complexity([1, 2, 3, 4]) == 1.75
    assert complexity([0 for _ in range(10000)]) == 1.9999

    # Test complexity of continuous domains
    domain = scipy.stats.uniform(loc=-7, scale=42)
    a, b = domain.interval(0.9999)
    c = 2 + np.linalg.norm(b - a)
    assert complexity(domain) == c

    domain = scipy.stats.norm(loc=-7, scale=42)
    a, b = domain.interval(0.9999)
    c = 2 + np.linalg.norm(b - a)
    assert complexity(domain) == c
