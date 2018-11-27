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

from pyrameter import Scope, ContinuousDomain, DiscreteDomain
import scipy.stats


def scope(*args, **kws):
    """Scope for joining multiple search domains.

    Parameters
    ----------
    <key> : `pyrameter.Domain`
        A search domain with a user-supplied name.

    Other Parameters
    ----------------
    exclusive : bool
        If True, members of this scope will be considered mutually exclusive
        and generated separately.
    optional : bool
        If True, members of this scope will be generated with 50%% probability
    """
    return Scope(*args, **kws)


# Uniform distribution
def uniform(lo, hi):
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
    return ContinuousDomain(scipy.stats.uniform, loc=lo, scale=hi,
                            callback=linear)


def ln_uniform(lo, hi):
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
    return ContinuousDomain(scipy.stats.uniform, loc=lo, scale=hi, callback=ln)


def log10_uniform(lo, hi):
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
    return ContinuousDomain(scipy.stats.uniform, loc=lo, scale=hi,
                            callback=log_10)


def log2_uniform(lo, hi):
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
    return ContinuousDomain(scipy.stats.uniform, loc=lo, scale=hi,
                            callback=log_2)


# Normal distribution
def normal(mu, sigma):
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
                            callback=linear)


def ln_normal(mu, sigma):
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
    return ContinuousDomain(scipy.stats.norm, loc=lo, scale=hi, callback=ln)


def log10_normal(mu, sigma):
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
                            callback=log_10)


def log2_normal(mu, sigma):
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
                            callback=log_2)


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
