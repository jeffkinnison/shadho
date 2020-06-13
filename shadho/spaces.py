"""Hyperparameter search space domain definitions.

Functions
---------
scope
    Create a scope to join multiple search domains.
uniform
    Create a continuous uniform distribution.
ln_uniform
    Create a natural-log-scaled continuous uniform distribution.
log10_uniform
    Create a log-10-scaled continuous uniform distribution.
log2_uniform
    Create a log-2-scaled continuous uniform distribution.
normal
    Create a normal distribution.
ln_normal
    Create a natural-log-scaled normal distribution.
log10_normal
    Create a log-10-scaled normal distribution.
log2_normal
    Create a log-2-scaled normal distribution.
randint
    Create a discrete integer domain.
log10_randint
    Create a log-10-scaled discrete integer domain.
log2_randint
    Create a log-2-scaled discrete integer domain.
choice
    Create a domain over a set of arbitrary categorical values.

See Also
--------
shadho.scaling
pyrameter.domain
"""
from shadho.scaling import linear, ln, log_10, log_2

import numpy as np
from pyrameter.domains import *
from pyrameter.specification import Specification
import scipy.stats


def scope(exclusive=False, optional=False, **kwargs):
    """Create a scope for hierarchical domain definitions.

    Hyperparameter search spaces can be set up as trees, with related
    hyperparameters grouped in subtrees. Scopes enable this type of
    organization.

    Parameters
    ----------
    exclusive : bool, optional
        If True, only generate a single hyperparameter (or sub-scope) from this
        scope at a time. Default ``False``.
    optional : bool, optional
        If True, either generate a set of hyperparameters from this scope or
        ignore the scope entirely. Default ``False``.
    domains
        Key/value pairs of domain names and valid SHADHO domains in this scope.

    Returns
    -------
    scope : `pyrameter.specification.Specification`
        The scope with all sub-domains.
    """
    return Specification(**kwargs)


# Uniform distribution
def uniform(lo, hi, **kwargs):
    """Continuous uniform distribution.

    The distribution is defined in range [``lo``, ``hi``].

    Parameters
    ----------
    lo : int, float
        Lower bound of the distribution.
    hi : int, float
        Upper bound of the distribution.

    Returns
    -------
    domain : `pyrameter.ContinuousDomain`
    """
    return ContinuousDomain(scipy.stats.uniform, loc=lo, scale=np.abs(hi - lo),
                            callback=linear, **kwargs)


def ln_uniform(lo, hi, **kwargs):
    """Natural log-scaled continuous uniform distribution.

    The distribution is defined in range [``lo``, ``hi``]. Sampled values ``x``
    are scaled by ``e**x`` before being returned.

    Parameters
    ----------
    lo : int, float
        Lower bound of the distribution.
    hi : int, float
        Upper bound of the distribution.

    Returns
    -------
    domain : `pyrameter.ContinuousDomain`
    """
    return ContinuousDomain(scipy.stats.uniform, loc=lo, scale=np.abs(hi - lo), callback=ln,
                            **kwargs)


def log10_uniform(lo, hi, **kwargs):
    """Log 10-scaled continuous uniform distribution.

    The distribution is defined in range [``lo``, ``hi``]. Sampled values ``x``
    are scaled by ``10**x`` before being returned.

    Parameters
    ----------
    lo : int, float
        Lower bound of the distribution.
    hi : int, float
        Upper bound of the distribution.

    Returns
    -------
    domain : `pyrameter.ContinuousDomain`
    """
    return ContinuousDomain(scipy.stats.uniform, loc=lo, scale=np.abs(hi - lo),
                            callback=log_10, **kwargs)


def log2_uniform(lo, hi, **kwargs):
    """Log 2-scaled continuous uniform distribution.

    The distribution is defined in range [``lo``, ``hi``]. Sampled values ``x``
    are scaled by ``2**x`` before being returned.

    Parameters
    ----------
    lo : int, float
        Lower bound of the distribution.
    hi : int, float
        Upper bound of the distribution.

    Returns
    -------
    domain : `pyrameter.ContinuousDomain`
    """
    return ContinuousDomain(scipy.stats.uniform, loc=lo, scale=np.abs(hi - lo),
                            callback=log_2, **kwargs)


# Normal distribution
def normal(mu, sigma, **kwargs):
    """Continuous normal distribution.

    Gaussian distribution parameterized with expected value ``mu`` and standard
    deviation ``sigma``.

    Parameters
    ----------
    mu : int, float
        Expected value of the distribution.
    sigma : int, float
        Standard deviation of the distribution.

    Returns
    -------
    domain : `pyrameter.ContinuousDomain`
    """
    return ContinuousDomain(scipy.stats.norm, loc=lo, scale=hi,
                            callback=linear, **kwargs)


def ln_normal(mu, sigma, **kwargs):
    """Natural log-scaled continuous normal distribution.

    Gaussian distribution parameterized with expected value ``mu`` and standard
    deviation ``sigma``. Sampled values ``x`` are scaled by ``e**x`` before
    being returned.

    Parameters
    ----------
    mu : int, float
        Expected value of the distribution.
    sigma : int, float
        Standard deviation of the distribution.

    Returns
    -------
    domain : `pyrameter.ContinuousDomain`
    """
    return ContinuousDomain(scipy.stats.norm, loc=lo, scale=hi, callback=ln,
                            **kwargs)


def log10_normal(mu, sigma, **kwargs):
    """Log 10-scaled continuous normal distribution.

    Gaussian distribution parameterized with expected value ``mu`` and standard
    deviation ``sigma``. Sampled values ``x`` are scaled by ``10**x`` before
    being returned.

    Parameters
    ----------
    mu : int, float
        Expected value of the distribution.
    sigma : int, float
        Standard deviation of the distribution.

    Returns
    -------
    domain : `pyrameter.ContinuousDomain`
    """
    return ContinuousDomain(scipy.stats.norm, loc=lo, scale=hi,
                            callback=log_10, **kwargs)


def log2_normal(mu, sigma, **kwargs):
    """Log 2-scaled continuous normal distribution.

    Gaussian distribution parameterized with expected value ``mu`` and standard
    deviation ``sigma``. Sampled values ``x`` are scaled by ``2**x`` before
    being returned.

    Parameters
    ----------
    mu : int, float
        Expected value of the distribution.
    sigma : int, float
        Standard deviation of the distribution.

    Returns
    -------
    domain : `pyrameter.ContinuousDomain`
    """
    return ContinuousDomain(scipy.stats.norm, loc=lo, scale=hi,
                            callback=log_2, **kwargs)


# Randint distributions
def randint(lo, hi, step=1):
    """Uniform distribution over a sequence of integers.

    The distribution is over the integer sequence [``lo``, ``hi``) with step
    ``step`` spacing.

    Parameters
    ----------
    lo : int
        Lower bound of the sequence.
    hi : int
        Upper bound of the sequence.
    step : int, optional
        Step between members of the sequence.

    Returns
    -------
    domain : `pyrameter.DiscreteDomain`
    """
    return DiscreteDomain(list(range(lo, hi, step)))


def ln_randint(lo, hi, step=1):
    """Natural log-scaled uniform distribution over a sequence of integers.

    The distribution is over the integer sequence [``lo``, ``hi``) with step
    ``step`` spacing. Sampled values ``x`` are scaled by ``e**x`` before
    being returned.

    Parameters
    ----------
    lo : int
        Lower bound of the sequence.
    hi : int
        Upper bound of the sequence.
    step : int, optional
        Step between members of the sequence.

    Returns
    -------
    domain : `pyrameter.DiscreteDomain`
    """
    return DiscreteDomain([ln(i) for i in range(lo, hi, step)])


def log10_randint(lo, hi, step=1):
    """Log 10-scaled uniform distribution over a sequence of integers.

    The distribution is over the integer sequence [``lo``, ``hi``) with step
    ``step`` spacing. Sampled values ``x`` are scaled by ``10**x`` before
    being returned.

    Parameters
    ----------
    lo : int
        Lower bound of the sequence.
    hi : int
        Upper bound of the sequence.
    step : int, optional
        Step between members of the sequence.

    Returns
    -------
    domain : `pyrameter.DiscreteDomain`
    """
    return DiscreteDomain([log_10(i) for i in range(lo, hi, step)])


def log2_randint(lo, hi, step=1):
    """Log 2-scaled uniform distribution over a sequence of integers.

    The distribution is over the integer sequence [``lo``, ``hi``) with step
    ``step`` spacing. Sampled values ``x`` are scaled by ``2**x`` before
    being returned.

    Parameters
    ----------
    lo : int
        Lower bound of the sequence.
    hi : int
        Upper bound of the sequence.
    step : int, optional
        Step between members of the sequence.

    Returns
    -------
    domain : `pyrameter.DiscreteDomain`
    """
    return DiscreteDomain([log_2(i) for i in range(lo, hi, step)])


# Choice
def choice(choices):
    """Random selection from an arbitrary set of values.

    This domain performs randint sampling from a set of aarbitrary values,
    allowing for randomly selecting strings, tuples, arbitrary collections of
    numbers, etc.

    Parameters
    ----------
    choices : list
        List of values to choose from.

    Returns
    -------
    domain : `pyrameter.DiscreteDomain`
    """
    return DiscreteDomain(choices)


# Exhaustive (a.k.a. Grid Search)
def exhaustive(choices):
    """Exhaustive search over a set of categorical values.

    Parameters
    ----------
    choices : list
        List of values to choose from.

    Returns
    -------
    domain : pyrameter.ExhaustiveDomain
    """
    return ExhaustiveDomain(choices)


def repeat(domain, repetitions, split=True):
    """Repeat a given domain a number of times.

    It can be helpful to repeat a domain a number of times, for example when
    iterating over a sequence of search spaces defined over the same values.
    If desired, the resulting domain can be split into ``repetitions``
    separate domains of length [1, 2, ..., ``repetitions``].

    Parameters
    ----------
    domain
        The domain to repeat, any valid SHADHO domain.
    repetitions : int
        The number of times to repeat the domain.
    split : bool
        If True, split the domain into ``repetitions`` sequences of domains of
        length [1, 2, ..., ``repetitions``]. If False, behaves like a single
        sequence. Default: True.

    Returns
    -------
    domain : pyrameter.RepeatedDomain
    """
    return RepeatedDomain(domain, repetitions, split=split)


def sequential(domains):
    """Construct a domain that behaves like a sequence when sampled.

    This domain consists of a tuple of domains that are sampled independently.
    When sampled, this will return a sequence of values in the same order as
    the provided domain sequence.

    Parameters
    ----------
    domains
        A list, tuple, or other sequence of valid SHADHO domains.
    
    Returns
    -------
    domain : pyrameter.SequenceDomain
    """
    return SequenceDomain(domains)


def dependent(domain, callback=None):
    return DependentDomain(domain, callback=lambda x: x if callback is None else callback)
