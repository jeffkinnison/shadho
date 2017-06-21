# -*- coding: utf-8 -*-
"""Strategies for exploring search spaces.

This module implements strategies for searching individual spaces. Strategies
are either undirected (as in `random`) or directed (`tpe`, `hyperband`, etc.).
A helper function has been included to provide a standard interface to access
these strategies for general use.

Functions
---------
get_strategy : function
    Retrieve a search strategy by name.
random : numeric
    Generate a random number (float or int) from a probability distribution.

"""


def get_strategy(name):
    """Retrieve a search strategy by name.

    This function is provided to allow easy access for regular use. Retrieves a
    search function that is defined within this module.

    Parameters
    ----------
    name : str
        The name of the strategy to get. Must be 'random'.

    Returns
    -------
    The requested search strategy function.

    """
    return random


def random(distribution, *args, **kwargs):
    """Randomly search a probability distribution.

    Random search is undirected beyond the specified probability distribution,
    returning a randomly generated value from the given distribution. Random
    search for hyperparameter optimization was suggested in [1].

    Currently, random search must be a subclass of scipy.stats.rv_continuous or
    scipy.stats.rv_discrete for consistency with the rest of this package.

    Parameters
    ----------
    distribution : scipy.stats.rv_continuous or scipy.stats.rv_discrete
        The probability distribution to draw from.
    *args : variable
        Arguments to parametrize the distribution.
    **kwargs : variable
        Keyword arguments to parametrize the distribution.

    Examples
    --------
    >>> random(scipy.stats.uniform)
    # Returns a value drawn from uniform distribution over [0.0, 1.0)
    >>> random(scipy.stats.uniform, loc=3.7, scale=5.0)
    # Returns a value drawn from uniform distribution over [3.7, 5.0)
    >>> random(scipy.stats.gamma, 3.2)
    # Returns a value from the gamma distribution with shape parameter a=3.2
    >>> random(scipy.stats.randint, -4, 8)
    # Returns an integer in the range [-4, 8)

    References
    ----------
    .. [1] J. Bergstra and Y. Bengio, "Random Search for Hyper-parameter
           Optimization," J. Mach. Learn. Res., Vol. 13, p. 281-305, 2012.
           
    """
    return distribution.rvs(*args, **kwargs)
