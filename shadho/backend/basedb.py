"""
"""
from ..heuristics import complexity, priority
from ..strategies import next_value
from ..scaling import scale_value

import copy
import numbers

import numpy as np
import scipy.stats


class BaseBackend(object):
    def split_spec(self, spec, path=''):
        """Split a specification into a forest of trees.

        Parameters
        ----------
        spec : dict
            The specification to build from.
        path : str
            The string denoting the curent place within the specification.

        Returns
        -------
        spaces : list of list of dict
            The set of disjoint search spaces created from this specification.

        Notes
        -----
        Instead of creating an explicit tree, this method takes advantage of
        the fact that 1) Python dictionary keys are unique to a particular
        dictionary and 2) keys from nested dictionaries can form a unique
        root-to-leaf path. Since a single hyperparameter search space is always
        a leaf in its tree, the entire tree can be reconstructed on-the-fly by
        keeping track of the search spaces it contains and storing the path to
        each space as an attribute in each space.

        In the long run, this saves memory and allows `shadho` to avoid
        pitfalls like the object creation memory leak in Python 2.
        """
        # Recursive base case.
        if not isinstance(spec, dict):
            spec = {
                'domain': spec,
                'strategy': 'random',
                'scaling': 'linear',
            }

        if all(key in spec for key in ('domain', 'strategy', 'scaling')):
            # Update spec directly to avoid creating new objects; returns the
            # reference to spec.
            spec['path'] = path
            return [[spec]]

        # Recurse through subtrees to create the path from root to leaf and
        # split into disjoint search spaces.
        exclusive = 'exclusive' in spec and spec['exclusive']
        optional = 'optional' in spec and spec['optional']
        spaces = [] if exclusive else [[]]
        for key in spec:
            if key not in ('exclusive', 'optional'):
                subpath = '/'.join([path, str(key)]) if path != '' \
                          else str(key)
                split = self.split_spec(spec[key], path=subpath)
                if exclusive:
                    spaces.extend(split)
                else:
                    newspaces = []
                    for space in spaces:
                        for s in split:
                            newspace = [c for c in space]
                            newspace.extend(s)
                            newspaces.append(newspace)
                    spaces = newspaces
        if optional:
            spaces.append([])
        return spaces

    def new_tree(self, *args, **kwargs):
        return BaseTree(*args, **kwargs)

    def new_space(self, *args, **kwargs):
        return BaseSpace(*args, **kwargs)

    def new_value(self, *args, **kwargs):
        return BaseValue(*args, **kwargs)

    def new_result(self, *args, **kwargs):
        return BaseResult(*args, **kwargs)


class BaseTree(object):
    def generate(self):
        """Generate a set of hyperparameter values.

        Returns
        -------
        params : dict
            Dictionary containing the generated hyperparameter values in their
            original tree structure.

        Notes
        -----
        The returned dictionary will never be flattened. This is to ensure that
        data is represented consistently throughout `shadho` within the master
        and workers. Ultimately, the user will expect their search to be
        structured the same way it was specified.
        """
        params = {}

        for space in self.spaces:
            path = space.path.split('/')
            curr = params
            for i in range(len(path) - 1):
                if path[i] not in curr:
                    curr[path[i]] = {}
                curr = curr[path[i]]
            curr[path[-1]] = space.generate()
        return params

    def calculate_priority(self):
        """Calculate the priority of searching this tree.

        The priority is a measure of the covariance between hyperparameter
        values and the resulting loss. Trees with a higher priority score will
        be allocated more searches on higher-performing hardware or a greater
        number of searches in the case that hardware is not specified.

        Notes
        -----
        The priority is stored internally in each instance of the Tree class.
        """
        try:
            feats = np.zeros((len(self.results), len(self.results[0].values)),
                             dtype=np.float64)
            losses = np.zeros((1, len(self.results)), dtype=np.float64)
        except IndexError:
            return

        for i in len(self.results):
            v = result.to_feature_vector()
            feats[i] += v[:-1]
            losses[i] += v[-1]

        self.priority = priority(feats, losses)

    def calculate_complexity(self):
        """Calculate the complexity of the search respresented by this tree.

        The complexity is an approximation of the size of the search as the sum
        of the size of each degree of freedom (leaf node). Trees with a higher
        complexity score will be allocated more searches on higher-performing
        hardware or a greater number of searches in the case that hardware is
        not specified.

        Notes
        -----
        The complexity is stored internally in each instance of the Tree class.

        See Also
        --------
        `shadho.heuristics.priority`
        """
        c = 0.0
        for space in self.spaces:
            c += space.complexity

        self.complexity = c

    @property
    def optimal_parameters(self):
        """Retrieve the parameters that result in an optimal loss.

        Returns
        -------
        loss : float
            The loss associated with the optimal parameters.
        params : dict
            The parameters that resulted in the optimal loss.

        See Also
        --------
        `shadho.heuristics.complexity`

        Notes
        -----
        This function returns the optimal parameters observed in a single tree
        instance. To compare across trees, acess this property once for each
        tree.
        """
        res = None
        for result in self.results:
            if res is None or result.loss < res.loss:
                res = result
        params = {}
        for value in res.values:
            path = value.space.path.split('/')
            curr = params
            for i in range(len(path) - 1):
                if path[i] not in curr:
                    curr[path[i]] = {}
                curr = curr[path[i]]
            curr[path[-1]] = value.value

        loss = res.loss if res is not None else None

        return (loss, params)


class BaseSpace(object):
    @property
    def complexity(self):
        """Calculate the complexity of searching this space.

        The complexity is an approximation of the size of the domain being
        searched.

        See Also
        --------
        `shadho.heuristics.complexity`
        """
        return complexity(self.domain)

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
        If the space is defined over a contiuous probability dristribution,
        returns a value from the random variate.

        If the space is defined over a discrete set of values, returns a
        randomly-selected value.

        If the space contains a single value, returns the value unaltered.
        """
        if hasattr(self.domain, 'dist') and \
           isinstance(self.domain.dist, scipy.stats.rv_continuous):
            value = scale_value(next_value(self.domain, self.strategy),
                                self.scaling)
        elif isinstance(self.domain, list) and len(self.domain) > 0:
            rv = scipy.stats.randint(low=0, high=len(self.domain))
            idx = next_value(rv, self.strategy)
            value = scale_value(self.domain[idx], self.scaling)
        else:
            value = self.domain

        return value


class BaseValue(object):
    def to_numeric(self):
        """Transform the value into its numeric representation.

        Returns
        -------
        The value of this object, transformed according to
        `shadho.backend.BaseSpace.get_label`

        See Also
        --------
        `shadho.backend.BaseSpace.get_label`
        """
        return self.space.get_label(self.value)


class BaseResult(object):
    def to_feature_vector(self):
        """Transform this result and its associated values into a vector.

        Returns
        -------
        v : `numpy.ndarray`
            A vector length n containing n - 1 hyperparameter values and their
            associated loss. Loss is stored in the last element.

        Notes
        -----
        There is no standardized order to the features across all runs of
        `shadho`, however for a particular run the features are ordered by the
        `id` attribute of the space that generated them. This ensures that the
        order always the same for a particular tree or set of search spaces.
        """
        v = np.zeros(len(self.values) + 1, dtype=np.float64)
        self.values.sort(key=lambda x: x.space_id)
        for i in range(len(self.values)):
            try:
                v[i] += self.values[i].to_numeric()
            except TypeError:
                continue
        try:
            v[-1] += self.loss
        except TypeError:
            # Happens in the case that result.loss is non-numeric
            pass
        return v
