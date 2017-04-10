"""Helper functions for instantiating hyperparameter spaces.

Functions
---------
uniform
ln_uniform
log10_uniform
log2_uniform
normal
ln_normal
log10_normal
log2_normal
randint
log10_randint
log2_randint
choose

See Also
--------
shadho.spaces.ContinuousSpace, shadho.spaces.DiscreteSpace
"""

from .spaces import ContinuousSpace, DiscreteSpace


# Uniform Continuous Distributions

def uniform(low, high, strategy='random', rng=None, seed=None):
    """Create a uniform distribution over the given range.

    Parameters
    ----------
    low : float
        The lower bound.
    high : float
        The upper bound.
    strategy : {'random', 'tpe', ...}, optional
        Search strategy to employ.
    rng : {None, numpy.random.RandomState}, optional
        The random number generator to use for drawing values from the
        uniform distribution.

    Returns
    -------
    space : shadho.spaces.ContinuousSpace
        The space containing the continuous uniform distribution defined over
        [low, high).
    """
    return ContinuousSpace(loc=low,
                           scale=high,
                           distribution='uniform',
                           strategy=strategy,
                           scaling='linear',
                           rng=rng,
                           seed=seed)


def ln_uniform(low, high, strategy='random', rng=None, seed=None):
    """Create a uniform distribution over the given range scaled by e^x.

    Parameters
    ----------
    low : float
        The lower bound.
    high : float
        The upper bound.
    strategy : {'random', 'tpe', ...}, optional
        Search strategy to employ.
    rng : {None, numpy.random.RandomState}, optional
        The random number generator to use for drawing values from the
        uniform distribution.

    Returns
    -------
    space : shadho.spaces.ContinuousSpace
        The space containing the continuous uniform distribution defined over
        [low, high) and scaled by e^x.
    """
    return ContinuousSpace(loc=low,
                           scale=high,
                           distribution='uniform',
                           strategy=strategy,
                           scaling='ln',
                           rng=rng,
                           seed=seed)


def log10_uniform(low, high, strategy='random', rng=None, seed=None):
    """Create a uniform distribution over the given range scaled by 10^x.

    Parameters
    ----------
    low : float
        The lower bound.
    high : float
        The upper bound.
    strategy : {'random', 'tpe', ...}, optional
        Search strategy to employ.
    rng : {None, numpy.random.RandomState}, optional
        The random number generator to use for drawing values from the
        uniform distribution.

    Returns
    -------
    space : shadho.spaces.ContinuousSpace
        The space containing the continuous uniform distribution defined over
        [low, high) and scaled by 10^x.
    """
    return ContinuousSpace(loc=low,
                           scale=high,
                           distribution='uniform',
                           strategy=strategy,
                           scaling='log10',
                           rng=rng,
                           seed=seed)


def log2_uniform(low, high, strategy='random', rng=None, seed=None):
    """Create a uniform distribution over the given range scaled by 2^x.

    Parameters
    ----------
    low : float
        The lower bound.
    high : float
        The upper bound.
    strategy : {'random', 'tpe', ...}, optional
        Search strategy to employ.
    rng : {None, numpy.random.RandomState}, optional
        The random number generator to use for drawing values from the
        uniform distribution.

    Returns
    -------
    space : shadho.spaces.ContinuousSpace
        The space containing the continuous uniform distribution defined over
        [low, high) and scaled by 2^x.
    """
    return ContinuousSpace(loc=low,
                           scale=high,
                           distribution='uniform',
                           strategy=strategy,
                           scaling='log2',
                           rng=rng,
                           seed=seed)


# Normal Distributions

def normal(mu, sigma, strategy='random', rng=None, seed=None):
    """Create a normal distribution over the given range.

    Parameters
    ----------
    mu : float
        The expected value of the distribution.
    sigma : float
        The variance of the distribution.
    strategy : {'random', 'tpe', ...}, optional
        Search strategy to employ.
    rng : {None, numpy.random.RandomState}, optional
        The random number generator to use for drawing values from the
        normal distribution.

    Returns
    -------
    space : shadho.spaces.ContinuousSpace
        The space containing the continuous normal distribution parameterized
        by (mu, sigma).
    """
    return ContinuousSpace(loc=mu,
                           scale=sigma,
                           distribution='norm',
                           strategy=strategy,
                           scaling='linear',
                           rng=rng,
                           seed=seed)


def ln_normal(mu, sigma, strategy='random', rng=None, seed=None):
    """Create a normal distribution over the given range and scaled by e^x.

    Parameters
    ----------
    mu : float
        The expected value of the distribution.
    sigma : float
        The variance of the distribution.
    strategy : {'random', 'tpe', ...}, optional
        Search strategy to employ.
    rng : {None, numpy.random.RandomState}, optional
        The random number generator to use for drawing values from the
        normal distribution.

    Returns
    -------
    space : shadho.spaces.ContinuousSpace
        The space containing the continuous normal distribution parameterized
        by (mu, sigma) and scaled by e^x.
    """
    return ContinuousSpace(loc=mu,
                           scale=sigma,
                           distribution='norm',
                           strategy=strategy,
                           scaling='ln',
                           rng=rng,
                           seed=seed)


def log10_normal(mu, sigma, strategy='random', rng=None, seed=None):
    """Create a normal distribution over the given range and scaled by 10^x.

    Parameters
    ----------
    mu : float
        The expected value of the distribution.
    sigma : float
        The variance of the distribution.
    strategy : {'random', 'tpe', ...}, optional
        Search strategy to employ.
    rng : {None, numpy.random.RandomState}, optional
        The random number generator to use for drawing values from the
        normal distribution.

    Returns
    -------
    space : shadho.spaces.ContinuousSpace
        The space containing the continuous normal distribution parameterized
        by (mu, sigma) and scaled by 10^x.
    """
    return ContinuousSpace(loc=mu,
                           scale=sigma,
                           distribution='norm',
                           strategy=strategy,
                           scaling='log10',
                           rng=rng,
                           seed=seed)


def log2_normal(mu, sigma, strategy='random', rng=None, seed=None):
    """Create a normal distribution over the given range and scaled by 2^x.

    Parameters
    ----------
    mu : float
        The expected value of the distribution.
    sigma : float
        The variance of the distribution.
    strategy : {'random', 'tpe', ...}, optional
        Search strategy to employ.
    rng : {None, numpy.random.RandomState}, optional
        The random number generator to use for drawing values from the
        normal distribution.

    Returns
    -------
    space : shadho.spaces.ContinuousSpace
        The space containing the continuous normal distribution parameterized
        by (mu, sigma) and scaled by 2^x.
    """
    return ContinuousSpace(loc=mu,
                           scale=sigma,
                           distribution='norm',
                           strategy=strategy,
                           scaling='log2',
                           rng=rng,
                           seed=seed)


# Discrete Distributions

def randint(low, high, step=1, strategy='random', rng=None, seed=None):
    """Draw random integers from the given range.

    Parameters
    ----------
    low : float
        The lower bound.
    high : float
        The upper bound.
    step : {1, int}, optional
        The step between values in the range.
    strategy : {'random', 'tpe', ...}, optional
        Search strategy to employ.
    rng : {None, numpy.random.RandomState}, optional
        The random number generator to use for drawing values from the
        uniform distribution.
    seed : {None, int}, optional
        The random seed to use.

    Returns
    -------
    space : shadho.spaces.DiscreteSpace
        The space containing sequential integers in range [low, high) separated
        by step.
    """
    r = sorted([low, high])
    return DiscreteSpace(values=list(range(*r, step)),
                         strategy=strategy,
                         scaling='linear',
                         rng=rng,
                         seed=seed)


def log10_randint(low, high, step=1, strategy='random', rng=None, seed=None):
    """Draw random integers from the given range, scaled by 10^x.

    Parameters
    ----------
    low : float
        The lower bound.
    high : float
        The upper bound.
    step : {1, int}, optional
        The step between values in the range.
    strategy : {'random', 'tpe', ...}, optional
        Search strategy to employ.
    rng : {None, numpy.random.RandomState}, optional
        The random number generator to use for drawing values from the
        uniform distribution.
    seed : {None, int}, optional
        The random seed to use.

    Returns
    -------
    space : shadho.spaces.DiscreteSpace
        The space containing sequential integers in range [low, high) separated
        by step, scaled by 10^x.
    """
    r = sorted([low, high])
    return DiscreteSpace(values=list(range(*r, step)),
                         strategy=strategy,
                         scaling='log10',
                         rng=rng,
                         seed=seed)


def log2_randint(low, high, step=1, strategy='random', rng=None, seed=None):
    """Draw random integers from the given range, scaled by 2^x.

    Parameters
    ----------
    low : float
        The lower bound.
    high : float
        The upper bound.
    step : {1, int}, optional
        The step between values in the range.
    strategy : {'random', 'tpe', ...}, optional
        Search strategy to employ.
    rng : {None, numpy.random.RandomState}, optional
        The random number generator to use for drawing values from the
        uniform distribution.
    seed : {None, int}, optional
        The random seed to use.

    Returns
    -------
    space : shadho.spaces.DiscreteSpace
        The space containing sequential integers in range [low, high) separated
        by step, scaled by 2^x.
    """
    r = sorted([low, high])
    return DiscreteSpace(values=list(range(*r, step)),
                         strategy=strategy,
                         scaling='log2',
                         rng=rng,
                         seed=seed)


# Choose One From Arbitrary Value Set

def choose(values, strategy='random', rng=None, seed=None):
    """Choose one of n categorical values.

    Parameters
    ----------
    values : list
        The finite set of values to search.
    strategy : {'random', 'tpe', ...}, optional
        Search strategy to employ.
    rng : {None, numpy.random.RandomState}, optional
        The random number generator to use for drawing values from the
        uniform distribution.
    seed : {None, int}, optional
        The random seed to use.

    Returns
    -------
    space : shadho.spaces.DiscreteSpace
        The space containing the supplied categorical values.
    """
    return DiscreteSpace(values=values,
                         strategy=strategy,
                         scaling='linear',
                         rng=rng,
                         seed=seed)
