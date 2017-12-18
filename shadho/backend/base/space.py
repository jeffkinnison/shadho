"""Facilities for working with hyperparameter search domains
"""
from shadho.heuristics import complexity
from shadho.strategies import next_value
from shadho.scaling import scale_value

import numbers

import numpy as np
import scipy.stats


class BaseDomain(object):
    """Base class for Domain data models."""

    @property
    def complexity(self):
        """Calculate the complexity of searching this space.

        The complexity is an approximation of the size of the domain being
        searched.

        See Also
        --------
        `shadho.heuristics.complexity`
        """
        return complexity(self.domain if not self.exhaustive
                          else self.domain[0])

    def get_label(self, value):
        """Transform categorical values into their numeric labels.

        Returns
        -------
        label : int or float
            If the space is categorical (e.g. ['foo', 'bar', 'baz'], [1, 2,
            3]), return the integer index of the categorical value.

            If the space is constant (e.g. 1, 'hello', None), return 0.

            If the space is a continuous space (e.g. a uniform distribution
            over a real-valued range), then simply return `value`.
        """
        try:
            if self.exhaustive:
                label = self.domain[0].index(value)
            else:
                label = self.domain.index(value)
        except (TypeError, AttributeError):
            if hasattr(self.domain, 'dist') and \
               isinstance(self.domain.dist, scipy.stats.rv_continuous):
                label = value if isinstance(value, (numbers.Number)) else -1
            else:
                label = 0 if value == self.domain or value is self.domain \
                        else -1
        except ValueError:
            label = -1
        return label

    def generate(self):
        """Generate a new value from this space.

        Returns
        -------
        value
            A value from this space's `domain` generated using the `strategy`
            and `scaling` functions specified in this space.

        Notes
        -----
        If the space is defined over a continuous probability dristribution,
        returns a value from the random variate.

        If the space is defined over a discrete set of values, returns a
        randomly-selected value.

        If the space contains a single value, returns the value unaltered.
        """
        if hasattr(self.domain, 'dist') and \
           isinstance(self.domain.dist, scipy.stats.rv_continuous):
            value = scale_value(next_value(self.domain, self.strategy),
                                self.scaling)
        elif self.exhaustive:
            if self.exhaustive_idx < len(self.domain):
                value = self.domain[self.exhaustive_idx]
                self.exhaustive_idx += 1
            else:
                value = None
        elif isinstance(self.domain, list) and len(self.domain) > 0:
            rv = scipy.stats.randint(low=0, high=len(self.domain))
            idx = next_value(rv, self.strategy)
            value = scale_value(self.domain[idx], self.scaling)
        else:
            value = self.domain

        return value
