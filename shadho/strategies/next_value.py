"""
"""
from .random_search import random_search

import warnings

import scipy.stats

STRATEGIES = {
    'random': random_search
}


def next_value(domain, strategy):
    """Generate a new value from a search domain.

    Parameters
    ----------
    domain : `scipy.stats.rv_continuous` or `scipy.stats.rv_discrete`
        The domain from which to generate a hyperparameter value.
    strategy : {'random'} or callable
        The `shadho.strategies` function to use to generate the new value or
        a custom function/callable object.

    Returns
    -------
    value
        The value generated from `domain` using `strategy`.

    Notes
    -----
    If `strategy` does not refer to a `shadho.strategies` function and cannot
    be called, this function resorts to using `shadho.strategies.random` by
    default.
    """
    try:
        value = STRATEGIES[strategy](domain) if strategy in STRATEGIES \
                else strategy(domain)
    except TypeError:
        msg = "Invalid strategy {}. Defaulting to random.".format(strategy)
        warnings.warn(msg)
        value = STRATEGIES['random'](domain)

    return value
