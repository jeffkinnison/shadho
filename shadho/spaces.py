# -*- coding: utf-8 -*-
"""Search space definitions for specifying hyperparameters.

Classes
-------
BaseSpace: base class for other spaces
ConstantSpace: search space containing a single search value
ContinuousSpace: search space defined over a real interval
DiscreteSpace: search space over a set of categorical values
"""
from . import strategies
from . import scales

import numpy as np
import scipy.stats


class DistributionDoesNotExist(Exception):
    pass


class BaseSpace(object):
    """Base class for other spaces."""

    def generate(self):
        """Generate a value from this space.

        The BaseSpace is defined over the Pythonic Nonespace, which consists of
        a single value (None). From this value, we catch a glimpse of the
        perfection and nihilistic delight that is eternity. Praise the None,
        for from it we are made whole.
        """
        return None

    def to_spec(self):
        """Generate the specification for this search space.

        The BaseSpace is defined over the Pythonic Nonespace, which consists of
        a single value (None). How does one specify the void? It may only be
        represented as the infinite yet incomprehensible None, as decreed by
        BDFL.
        """
        return None

    def complexity(self):
        """Determine the complexity of the search space.

        The BaseSpace is defined over the Pythonic Nonespace, which consists of
        a single value (None). According to the ``scriptures<https://docs.python.org/3/reference/datamodel.html#the-standard-type-hierarchy>``_
        None is singular and infinite, representing the identity and lack of
        identity simultaneously. Our feeble human minds cannot comprehend this
        duality, and thus we represent None as 1 for the sake of the Algorithm.
        """
        return 1

    def __str__(self):
        return str(None)


class ConstantSpace(BaseSpace):
    """A search space containing a single value.

    This space exists to unify the API for generating search values, allowing
    users to submit standard but arbitrary information along with searches.

    Parameters
    ----------
    value : type
        The constant value stored within this space.

    """

    def __init__(self, value):
        super(ConstantSpace, self).__init__()
        self.value = value

    def generate(self):
        """Generate a value from this space.

        Returns the constant value stored within this space.
        """
        return self.value

    def to_spec(self):
        """Generate the specification for this search space.

        This space is specified entirely by a single value.
        """
        return self.value

    def __str__(self):
        return str(self.value)


class ContinuousSpace(BaseSpace):
    """A continuous real interval fit to a probability distribution.

    Parameters
    ----------
    *args : tuple
        The tuple containing arbitrary arguments for use with the probability
        distribution.
    distribution : {str, scipy.stats.rv_continuous}, optional
        The name of the probability distribution or a subclass of the scipy
        base continuous probability distribution.
    strategy : {'random', 'tpe', ...}, optional
        The search strategy to use, as defined in shadho.strategies
    scaling : {'linear', 'ln', 'log10', 'log2'}, optional
        The scaling function to apply to generated values.
    rng : {None, numpy.random.RandomState}, optional
        The random number generator to use. `None` will create a new RNG seeded
        by `seed`.
    seed : {None, int, array_like}, optional
        Random seed to use with `rng`. See the ``numpy.random.RandomState
        documentation<https://docs.scipy.org/doc/numpy/reference/generated/numpy.random.RandomState.html#numpy.random.RandomState>``_ for details.
    **kwargs : dict
        Arbitrary additional key/value pairs for use with the probability
        distribution.

    Raises
    ------
    DistributionDoesNotExist
        Raised when the supplied probability distribution is not a standard
        scipy.stats distribution or not a subclass of scipy.stats.rv_continuous

    """

    def __init__(self, distribution='uniform', strategy='random',
                 scaling='linear', rng=None, seed=None, *args, **kwargs):
        # Get the scipy distribution by attribute name. If not an existing
        # attribute, check to see if a subclass of scipy.stats.rv_continuous.
        #
        try:
            self.distribution = getattr(scipy.stats, distribution)
        except AttributeError:
            if isinstance(distribution, scipy.stats.rv_continuous):
                self.distribution = distribution
            else:
                raise DistributionDoesNotExist(str(distribution))

        # Save the args and kwargs for use with self.distribution
        self.dist_args = args
        self.dist_kwargs = kwargs

        # Get the search strategy and scaling funtion from their respective
        # modules.
        self.strategy = strategies.get_strategy(strategy)
        self.scale = scales.get_scale(scaling)

        # Information for recreating the specification.
        self.dist_name = distribution if isinstance(distribution, str) \
            else 'custom'
        self.strategy_name = strategy
        self.scale_name = scaling

        self.rng = rng if rng is not None else np.random.RandomState(seed)

    def generate(self):
        """Generate a value from this space.

        Returns a random value from the probability distribution based on the
        search strategy and scaled by the scaling function.
        """
        return self.scale(self.strategy(self.distribution,
                                        random_state=self.rng,
                                        *self.dist_args,
                                        **self.dist_kwargs))

    def to_spec(self):
        """Generate the specification for this search space.

        This space is specified by its probability distribution, search
        strategy, and scaling function. This function allows the space to be
        saved for checkpointing and analysis.
        """
        state = self.rng.get_state()
        return {
            'distribution': self.dist_name,
            'args': self.dist_args,
            'kwargs': self.dist_kwargs,
            'strategy': self.strategy_name,
            'scale': self.scale_name,
            'random_state': [
                state[0],
                list(state[1]),
                state[2],
                state[3],
                state[4]
            ]
        }

    def complexity(self):
        """Determine the complexity of the search space.

        The complexity is defined as

        ..math::

            2 + \|b - a\|

        where (a, b) is the interval containing 99%% of the probability
        distribution.
        """
        interval = self.distribution.interval(.99,
                                              *self.dist_args,
                                              **self.dist_kwargs)
        distance = np.linalg.norm(interval[1] - interval[0])
        return 2 + distance

    def __str__(self):
        return str(self.to_spec())


class DiscreteSpace(BaseSpace):
    """A set of categorical values to be searched.

    Parameters
    ----------
    *args : tuple
        The tuple containing arbitrary arguments for use with the probability
        distribution.
    values : {None, list}
        The set of discrete value to search.
    strategy : {'random', 'tpe', ...}, optional
        The search strategy to use, as defined in shadho.strategies
    scaling : {'linear', 'ln', 'log10', 'log2'}, optional
        The scaling function to apply to generated values.
    rng : {None, numpy.random.RandomState}, optional
        The random number generator to use. `None` will create a new RNG seeded
        by `seed`.
    seed : {None, int, array_like}, optional
        Random seed to use with `rng`. See the ``numpy.random.RandomState
        documentation<https://docs.scipy.org/doc/numpy/reference/generated/numpy.random.RandomState.html#numpy.random.RandomState>``_ for details.
    **kwargs : dict
        Arbitrary additional key/value pairs for use with the probability
        distribution.
    """
    def __init__(self, values=None, strategy='random', scaling='linear',
                 rng=None, seed=None, *args, **kwargs):
        self.values = values if values is not None else []

        self.distribution = scipy.stats.randint
        self.dist_args = [0, len(self.values)]
        self.dist_kwargs = kwargs
        self.strategy = strategies.get_strategy(strategy)
        self.scale = scales.get_scale(scaling)
        self.strategy_name = strategy
        self.scale_name = scaling
        self.rng = rng if rng is not None else np.random.RandomState(seed)

    def generate(self):
        """Generate a value from this space.

        Returns a random value from the set of possible values based on the
        search strategy and scaled by the scaling function.
        """
        if len(self.values) == 0:
            return None
        idx = self.strategy(self.distribution,
                            random_state=self.rng,
                            *self.dist_args,
                            **self.dist_kwargs)
        return self.scale(self.values[idx])

    def to_spec(self):
        """Generate the specification for this search space.

        This space is specified by its set of values, search strategy, and
        scaling function. This function allows the space to be saved for
        checkpointing and analysis.
        """
        state = self.rng.get_state()
        return {
            'values': self.values,
            'strategy': self.strategy_name,
            'scale': self.scale_name,
            'random_state': [
                state[0],
                list(state[1]),
                state[2],
                state[3],
                state[4]
            ]
        }

    def complexity(self):
        """Determine the complexity of the search space.

        The complexity is defined as

        ..math::
            1 + |self.values|
        """
        return 1.0 + (1.0 - (1.0 / float(len(self.values)))) \
            if len(self.values) > 0 else 1

    def __str__(self):
        return str(self.to_spec())
